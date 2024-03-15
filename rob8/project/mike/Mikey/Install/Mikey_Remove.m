%% Find the root level dir
currentDir = mfilename('fullpath');
rootDirIdx = strfind(currentDir,'Install');
rootDir = currentDir(1:rootDirIdx(end)-2);
%% Remove the install path from the search directory  
if exist([rootDir, '\Install\', 'installPath.mat'],'file') == 2
    %% 
    display('REMOVING MichelangeloHand: Removing the obsolete paths ...')
    load ([rootDir, '\Install\', 'installPath.mat']);
    rmpath(installPath);
    currentPath = pathdef();
    % Remove the obsolete paths
    pathStrings = strsplit(currentPath,';');
    doesPathExist = cellfun(@(x) exist(x,'dir'), pathStrings);
    pathNotOK = find(doesPathExist == 0);
    for i = pathNotOK
        rmpath(pathStrings{i});
    end
    currentPath = path();
    path(currentPath);
    display('REMOVING MichelangeloHand: Removing the search path ...')
    if savepath
        error('You need administrator privilegies in order to perform this operation!');
    else
        delete([rootDir, '\Install\', 'installPath.mat']);
        display('REMOVING MichelangeloHand: Finished!')
    end
else
    display('REMOVING MichelangeloHand: There are no previosly installed versions!')
end
%% Clear the variables
clear currentPath installPath libBrow currentDir rootDirIdx rootDir
clear pathStrings doesPathExist pathNotOK