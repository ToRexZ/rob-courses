clc
classdef michelangeloHand < handle
    properties (SetAccess = private)
        sensVal = []; % // Main drive angle, thumb angle, grip force, Main drive current, thumb current, rotation angle, extension angle, rotation current, flexion current
        EMG = []; % // Ch1 .. Ch8
        physVal = []; % // Grasp Type, hand aperture in cm, rotation and flexion in degrees, force in %
        statusFlags = [];
        
        commMonitor = [];
        Fs = 20;
        bufferSize = []; % It will be automatically adjusted to fit 120 of slow and 60 minutes of fast dump
        acqMode = 'SensorsEMG';
        dongleSpeed = 'fast';
        MH = [];
          
        debugMode = 3
       
        desiredPhysVal = [];
        desiredSensVal = [];
        issuedCmds = [];
    end
    
    events
        NewDataAvaliable
    end
    
    methods(Access = public)
        %% INITIALIZATION FUNCTIONS
        function obj = michelangeloHand(varargin)
            try
                currentDir = which('michelangeloHand.m');
                currentDir = currentDir(1:end-length('michelangeloHand.m'));
                addpath([currentDir 'DLLs']);
                addpath([currentDir 'Calibration']);
                % Check for existance of .NET assembly
                FilePath = [currentDir 'DLLs\MichelangeloComLib.dll'];
                if (exist(FilePath,'file')~=2)
                    obj.messageHandler('error', 'The .NET assembly path is not valid. Change the value of FilePath variable');
                end
                % Check if the instance of the same object exists in memory
                varList = evalin('base', 'who()');
                for i=1:numel(varList)
                    tempVar = varList{i};
                    if evalin('base', ['isa(' ,tempVar ,', ''michelangeloHand'') && isvalid(', tempVar  ,')']) 
                         obj.messageHandler('notify', 'An instance of the michelangelo class already exists in the memory ... Deleting ...');    
                        evalin('base',[tempVar, '.delete()'])
                    end
                end
                % Check for the inputs validity
                narginchk(0,8); % Check for the number of arguments
                if ~isempty(varargin)
                    numArg = size(varargin,2);
                    for i=1:2:numArg
                        paramName = varargin{i};
                        switch paramName
                            case 'DumpMode'
                                if ~(strcmpi('SensorsEMG', varargin{i+1}) || strcmpi('Sensors', varargin{i+1}) || strcmpi('EMG', varargin{i+1}))
                                    obj.messageHandler('warning','Acquisition mode must be on of the following: SensorsEMG, Sensors, EMG');
                                else
                                    obj.acqMode = varargin{i+1};
                                end
                            case 'DongleSpeed'
                                if ~(strcmpi('slow', varargin{i+1}) || strcmpi('fast', varargin{i+1}))
                                    obj.messageHandler('warning','Dongle speed must be on of the following: Slow, Fast');
                                else
                                    obj.dongleSpeed = varargin{i+1};
                                end
                            case 'PullFrequency'
                                if varargin{i+1} < 10 || varargin{i+1} > 100
                                    obj.messageHandler('warning', 'Sample frequency must be an integer ranging from 10 to 100 Hz')
                                else
                                    obj.Fs = round(varargin{i+1});
                                end
                            case 'DebugMode'
                                obj.debugMode = varargin{i+1};
                            otherwise
                                obj.messageHandler('error', ['Unknown parameter ''' paramName '''. Parameters are ''DumpMode'', ''DongleSpeed'', ''PullFrequency'' and ''DebugMode''']);
                        end
                    end
                end
                obj.messageHandler('notify', ['Sample freq: ' num2str(obj.Fs,3) '. Acquisition mode: ', ...
                    obj.acqMode '. Debug level of detail: ' num2str(obj.debugMode,3)  '. Dongle speed: ' obj.dongleSpeed]);
                % Connect
                obj.messageHandler('notify', 'Connecting to the prosthesis');
                NET.addAssembly(FilePath);
                Mike = MichelangeloProsthesis.Michelangelo.start();
                try
                    % Configuration parameters
                    Mike.setDongleSpeed(obj.dongleSpeed);
                    Mike.useLessCPU = true;
                    Mike.Connect();
                catch ME
                    Mike.Disconnect();
                    delete(Mike);
                    obj.messageHandler('error','Connection unsuccessful! .NET Failure!');
                    return
                end
                Timer_start = tic; RetryCount = 0;
                while Mike.ConnectedFlag == 0
                    time = toc(Timer_start);
                    pause(0.3);
                    if time > 45
                        Mike.Disconnect();
                        delete(Mike);
                        obj.messageHandler('error','Connection timeout! Make sure you are: 1) In the bluetooth mode 2) Using the apropriate dongle speed. 3) Not already connected');
                    end
                    if ~isempty(strfind(char(Mike.ErrorMessage), 'overflow')) 
                        RetryCount = RetryCount +1;
                        obj.messageHandler('warning',['Something went wrong! Retrying: ' num2str(RetryCount) ' ...']);
                        Mike.Disconnect();
                        delete(Mike);
                        Timer_start = tic;
                        NET.addAssembly(FilePath);
                        Mike = MichelangeloProsthesis.Michelangelo.start();
                        Mike.useLessCPU = true;
                        Mike.Connect();  
                    end
                end
                % Data transfer
                switch obj.acqMode
                    case 'SensorsEMG'
                        Mike.FastSpecialDumpEvent = false; % set the fast transmission OFF
                        Mike.DumpSEMGData = true; % set the EMG transmission ON
                        Mike.DumpSensorData = true; % set the Sensor transmission ON;
                        Mike.setEMGAndSensorDump();
                        obj.bufferSize = 100 * 60 * 120; % buffer fits 2h of continous recording (100 Hz)
                        Mike.SetRecordBufferSize(obj.bufferSize);
                    case 'Sensors'
                        Mike.FastSpecialDumpEvent = false; % set the fast transmission OFF
                        Mike.DumpSEMGData = false; % set the EMG transmission OFF
                        Mike.DumpSensorData = true; % set the Sensor transmission ON;
                        Mike.setEMGAndSensorDump();
                        obj.bufferSize = 100 * 60 * 120; % buffer fits 2h of continous recording (100 Hz)
                        Mike.SetRecordBufferSize(obj.bufferSize);
                    case 'EMG'
                        Mike.FastSpecialDumpEvent = true; % set the fast transmission ON
                        Mike.DumpSEMGData = true; % set the EMG transmission ON
                        Mike.DumpSensorData = false; % set the Sensor transmission OFF;
                        Mike.setOnlyEMGFast();
                        obj.bufferSize = 1000 * 60 * 60; % buffer fits 1h of continous recording (1Khz)
                        Mike.SetRecordBufferSize(obj.bufferSize);
                end
                Timer_start = tic;
                while Mike.DumpConfigFailed
                    pause(0.5)
                    time = toc(Timer_start);
                    if time > 10 %
                        Mike.Disconnect();
                        delete(Mike);
                    end
                end
                pause(0.5);
                obj.MH = Mike;
                % Add listeners, setup readout timer
                obj.commMonitor = timer('TimerFcn', {@michelangeloHand.commMonitorFcn, obj}, ...
                    'ExecutionMode','fixedRate','Period', 1/obj.Fs, 'BusyMode', 'drop');
                obj.messageHandler('success','Mikey is ready to go :)');
            catch ME
                obj.delete();
                rethrow(ME)
            end
        end
        
        % Destructor
        function delete(obj)
            try
                obj.stopMonitoring();
                delete(obj.commMonitor);               
                obj.MH.Disconnect();
                delete(obj.MH);
                obj.messageHandler('success','Mikey disconnected :(');
                pause(0.75);
            end
        end
        
        function result = clearMemory(obj)
            result1 = obj.MH.ClearMemory();
            result2 = obj.MH.InitMemory();
            result = result1 && result2;
            if (result)
                obj.messageHandler('success', 'Memory clear OK');
            else
                obj.messageHandler('warning', char(obj.MH.ErrorMessage));
            end
        end
        
        function result = setRecordBufferSize(obj, size)
            result = obj.MH.SetRecordBufferSize(size);
            if (result)
                obj.bufferSize = size;
                obj.messageHandler('success', 'Dump buffer size change OK');
            else
                obj.messageHandler('warning', char(obj.MH.ErrorMessage));
            end
        end
        
        %% COMMUNICATION PORTS      
        function closeComm(obj)
            if single(obj.MH.CommunicationPortIsOpen)
                obj.MH.stopCommunication();
                pause(0.1);
            end
        end
        
        function openSerialComm(obj, PortName, BaudRate)
            obj.closeComm();
            % temorary workoaround
            obj.MH.setCommunicationProtocol(1);
            obj.MH.UdpSenderHost = '127.0.0.1';
            obj.MH.UdpPortReceive = 8051;
            obj.MH.startCommunication();
            obj.closeComm();
            %
            obj.MH.setCommunicationProtocol(0);
            obj.MH.SerialComportBaudrate = BaudRate;
            obj.MH.SerialComportName = PortName;
            obj.MH.startCommunication();
        end

        function openUDPComm(obj, Host, Port)
            obj.closeComm();
            % temorary workoaround
            %serialInfo = instrhwinfo('serial');
            %obj.MH.setCommunicationProtocol(0);
            %obj.MH.SerialComportBaudrate = 9600;
            %obj.MH.SerialComportName = serialInfo.AvailableSerialPorts{1};
            %obj.MH.startCommunication();
            %obj.closeComm();
            %
            obj.MH.setCommunicationProtocol(1);
            obj.MH.UDPfastRead = true;
            obj.MH.UdpSenderHost = Host;
            obj.MH.UdpPortReceive = Port;
            obj.MH.startCommunication();
        end
        
        %% PARAMETER CHANGE FUNCTIONS
        function setSampleRate(obj, Fs)
            obj.Fs = Fs;
            if strcmp(obj.commMonitor.Running,'on')
                obj.stopMonitoring();
                set(obj.commMonitor, 'Period', 1/obj.Fs);
                obj.startMonitoring();
            else
                set(obj.commMonitor, 'Period', 1/obj.Fs);
            end
        end
        
        function setDebugMode(obj, debugMode)
            if (debugMode>=1)  && (debugMode<=3)
                obj.messageHandler('notify', ['The debug debug mode has been set to: ' num2str(debugMode,2)]);
                obj.debugMode = debugMode;
            else
                obj.messageHandler('warning', 'Ilegal parameter value for the debug mode');
            end
        end
        
        
        function result = reCalibrate(obj, fullFilePath)
            result = obj.MH.LoadConfigFromXML(fullFilePath);
            if result
                obj.messageHandler('success', 'XML Calibration file load OK');
            else
                obj.messageHandler('warning', char(obj.MH.ErrorMessage));
            end
        end
        
        %% COMMAND INTERFACE FUNCTIONS
        function reachPreshape(obj, varargin)
            if strcmp(obj.acqMode,'SensorsEMG') || strcmp(obj.acqMode,'Sensors')
                numArg = size(varargin,2);
                if mod(numArg,2)
                    obj.messageHandler('warning', 'Arguments must be provided in pairs (name, value). Ignorring extra entries');
                end
                commands = zeros(1,7,'single');
                commands(5:7) = 255;
                physVal = single(obj.MH.PhysicalValues);
                commands(1) =  physVal(1);
                commands(2) = physVal(2);
                commands(3) = physVal(3);
                commands(4) = physVal(4);
                for i = 1:2:numArg
                    paramName = varargin{i};
                    switch paramName
                        case 'graspType'
                            if strcmp(varargin{i+1},'lateral');
                                commands(1) = 1;
                            elseif strcmp(varargin{i+1},'palmar')
                                commands(1) = 0;
                            end
                        case 'aperture'
                            commands(2) = varargin{i+1};
                        case 'rotation'
                            commands(3) = varargin{i+1};
                        case 'flexion'
                            commands(4) = varargin{i+1};
                        case 'speedH'
                            commands(5) = varargin{i+1};
                        case 'speedR'
                            commands(6) = varargin{i+1};
                        case 'speedF'
                            commands(7) = varargin{i+1};
                    end
                end
                obj.MH.reachPreshape(commands(1:4), commands(5:7));
            else
                obj.messageHandler('warning', 'Position control is avaliable only in 100 Hz mode');
            end
        end
        
        function reachPosition(obj, varargin)
            if strcmp(obj.acqMode,'SensorsEMG') || strcmp(obj.acqMode,'Sensors')
                numArg = size(varargin,2);
                if mod(numArg,2)
                    obj.messageHandler('warning', 'Arguments must be provided in pairs (name, value). Ignorring extra entries');
                end
                commands = Inf(1,7,'single');
                physVal = single(obj.MH.PhysicalValues);
                commands(1) =  physVal(1);
                commands(2) = physVal(2);
                commands(3) = physVal(3);
                commands(4) = physVal(4);
                for i = 1:2:numArg
                    paramName = varargin{i};
                    switch paramName
                        case 'graspType'
                            if strcmp(varargin{i+1},'lateral');
                                commands(1) = 1;
                            elseif strcmp(varargin{i+1},'palmar')
                                commands(1) = 0;
                            end
                        case 'aperture'
                            commands(2) = varargin{i+1};
                        case 'rotation'
                            commands(3) = varargin{i+1};
                        case 'flexion'
                            commands(4) = varargin{i+1};
                        case 'speedH'
                            commands(5) = varargin{i+1};
                        case 'speedR'
                            commands(6) = varargin{i+1};
                        case 'speedF'
                            commands(7) = varargin{i+1};
                    end
                end
                obj.MH.reachPreshape(commands);
            else
                obj.messageHandler('warning', 'Position control is avaliable only in 100 Hz mode');
            end
        end
        
        function reachVelocity(obj, command)
            command = uint8(command);
            obj.MH.simultaneousMovement(command(1), command(2), command(3), command(4), command(5), command(6), command(7));
        end
        
        function reachNeutralPreshape(obj)
            obj.MH.reachNeutral();
        end
        
        function stopMovement(obj)
            command = zeros(1,7,'uint8');
            obj.reachVelocity(command);
        end
        
        %% STATE PULLING FUNCTIONS
        function startMonitoring(obj)
            if strcmp(obj.commMonitor.Running,'off')
                obj.messageHandler('notify', 'The data dump has started');
                start(obj.commMonitor);
                obj.MH.StartDump();
            end
        end
        
        function stopMonitoring(obj)
            if strcmp(obj.commMonitor.Running,'on') || logical(obj.MH.DumpStarted)
                obj.messageHandler('notify', 'The data dump has stopped');
                obj.MH.StopDump();
                stop(obj.commMonitor);
            end
        end
        
        function getSampleRate(obj)
            obj.messageHandler('notify',['The desired data pull rate is: ' num2str(obj.Fs,3)]);
            obj.messageHandler('notify',['The average data pull rate is: ' num2str(round(1/obj.commMonitor.AveragePeriod),3)]);
        end
        
    end
    
    methods (Access = private)

        function messageHandler(obj, msgType, msgStr)
            switch true
                case strcmp(msgType,'notify') && (obj.debugMode >= 2)
                    msgCol = [0.2 0.4 0.9];
                    cprintf(msgCol,[msgStr, '...\n']);
                case  strcmp(msgType,'error')
                    error([msgStr, '!?\n']);
                case  strcmp(msgType,'warning') && (obj.debugMode >= 1)
                    msgCol = [0.9 0.5 0.1];
                    cprintf(msgCol,[msgStr, '!\n']);
                case  strcmp(msgType,'success') && (obj.debugMode == 3)
                    msgCol = [0.4 0.75 0.2];
                    cprintf(msgCol,[msgStr '\n']);
            end
        end
        
    end
    
    methods (Access = private, Static)
        
        function commMonitorFcn(~, ~, obj)
            
            % Read a new chunck of EMG data
            if strcmp(obj.acqMode,'SensorsEMG') || strcmp(obj.acqMode,'EMG')
                temp = single(obj.MH.GetEMGData);
                if ~isempty(temp)
                    obj.EMG = reshape(temp, obj.MH.NumberOfChannels, size(temp,2)/obj.MH.NumberOfChannels);
                else
                    return; % do nothing
                end
            end
            % Retrieve a new chunk of Sensory data
            if strcmp(obj.acqMode,'SensorsEMG') || strcmp(obj.acqMode,'Sensors')
                temp1 = single(obj.MH.GetSensorData);
                temp2 = single(obj.MH.GetPhysicalData);
                if (~isempty(temp1) && ~isempty(temp2))
                    obj.sensVal = reshape(temp1, obj.MH.NumberOfSensors, size(temp1,2)/obj.MH.NumberOfSensors);
                    obj.physVal = reshape(temp2, obj.MH.NumberOfPhysical, size(temp2,2)/obj.MH.NumberOfPhysical);
                else
                    return % do nothing
                end
            end
            
            % Notify the connected listeners
            notify(obj, 'NewDataAvaliable');
            %% Area debugging
%             persistent numEMG numSens numPhys
%             if isempty(numEMG)
%                 numEMG = 0;
%                 numSens = 0;
%                 numPhys = 0;
%             end
%             
%             numEMG = numEMG + size(temp,2)/obj.MH.NumberOfChannels;
%             numSens = numSens + size(temp1,2)/obj.MH.NumberOfSensors;
%             numPhys = numPhys + size(temp2,2)/obj.MH.NumberOfPhysical;
%             
%             display(['Total number of samples: '  num2str(single(obj.MH.TimesEndOfBufferWasReached)*single(obj.MH.RecordBufferSize) + single(obj.MH.RecordBufferPointer))]);
%             display(['Gathered EMG  samples: ' num2str(numEMG)]);
%             display(['Gathered SENS samples: ' num2str(numSens)]);
%             display(['Gathered PHYS samples: ' num2str(numPhys)]);
            %% 
            
        end
          
    end
    
end