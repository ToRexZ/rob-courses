% Check the minimal system requirements
if ~strcmp(computer('arch'),'win64') || isempty(dir('C:\Windows\Microsoft.NET\Framework64'))
    error('You need to be running 64bit version of Windows with .NET framework installed');
end

% Remove the CLS from the matlab search path
display('INSTALLING MichelangeloHand: Removing previos versions ...')
Mikey_Remove

%% Find the root level dir 
currentDir = mfilename('fullpath');
rootDirIdx = strfind(currentDir,'Install');
rootDir = currentDir(1:rootDirIdx(end)-2);

%% Add each of the dirs to the matlab search path
display('INSTALLING MichelangeloHand: Adding directory trees ...')
currentPath = pathdef();
validDirs  = {'AdditionalDependicies', 'DLLs', 'Calibration'};
installPath = [];
for i = 1:length(validDirs)
    folderS = [rootDir, '\', validDirs{i}, ';'];
    installPath = [installPath folderS];
    path(folderS,currentPath);
    currentPath = path();
    % Register assembly
    if strcmp(validDirs{i}, 'DLLs')
        display('INSTALLING MichelangeloHand: Registering the .DLLs ...')
        dllPath = [rootDir, '\', validDirs{i} '\MichelangeloComLib.dll'];
        % determine the highest version of .NET installed
        netPath = dir('C:\Windows\Microsoft.NET\Framework64');
        verNet = 0;
        for j=1:length(netPath)
            if netPath(j).name(1) == 'v'
                numStr = strrep(netPath(j).name(2:end),'.','');
                numDig = length(numStr)-1;
                if str2num(numStr)/10^numDig > verNet
                    verNet = str2num(numStr)/10^numDig;
                    verNetIdx = j;
                end
            end
        end
        
        if verNet < 4
            error('You need to have at least .NET v4.0');
        end
        
        % Unregister old components
        display('INSTALLING MichelangeloHand: PRESS ENTER ...')
        netPath = ['C:\Windows\Microsoft.NET\Framework64\' netPath(verNetIdx).name];
        if exist([rootDir, '\', validDirs{i} '\MichelangeloComLib.tlb'], 'file')
            system (['powershell "start -FilePath "' netPath, '\RegAsm.exe"' ' -ArgumentList ''' dllPath ' /unregister'' -verb runAs"']);
            delete([rootDir, '\', validDirs{i} '\MichelangeloComLib.tlb']);
        end
        display('INSTALLING MichelangeloHand: PRESS ENTER ...')
        % Register new components
        registrationOK =  system (['powershell "start -FilePath "' netPath, '\RegAsm.exe"' ' -ArgumentList ''' dllPath ' /tlb'' -verb runAs"']);
        pause(2);
        if registrationOK ~= 0 || ~exist([rootDir, '\', validDirs{i} '\MichelangeloComLib.tlb'], 'file')
            error(sprintf('Something went wrong while trying to register the .NET component:\n 1) Run MATLAB with admin privilegies. \n 2) Check that there are no white spaces in the dir path.'));
        end        
        
    end

end
path(rootDir,currentPath);
currentPath = path();

%% Save the current search path
display('INSTALLING MichelangeloHand: Saving new search path ...')
if savepath
    error('You need administrator privilegies in order to perform this operation!');
else
    save([rootDir, '\Install\', 'installPath.mat'], 'installPath')
    display('INSTALLING MichelangeloHand: Finished!')
end

%% Clear the variables
clear currentDir fileName rootDirIdx rootDir folderS currentPath installPath dirs i validDirs