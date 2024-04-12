%clear
clc; close all
itert = 5000; % number of iteractions
shi = 5000; % show results every 5000 iteractions (can be less if desired)

X = S1_EMGflt(:,1:32); % experimental data (all 32 channels)
X = mean(X,3); % averaging across trials

%% data normalization (from 0 to 1 in all channels)
for vf = 1:size(X,2)
    ORIG(:,vf) = mat2gray(X(:,vf));
end

%% Processing NMF for averaged EMG
figure(1)
for n_mol=1:size(ORIG,2)
    display(['NMF analysis for averaged EMG ' num2str(n_mol) ' synergies...'])
    
    [W,H,E]=nmf_mm(ORIG,n_mol,itert,shi);
    REC=W*H; % reconstructed signal based on W and H for each number of synergies (features)
    
    %% calculating VAF for each muscle
    % VAF = 1 ? SSE/SST, where  SSE(sum of squared errors)is the unexplained variation
    %                           SST(total sum of squares) is the pooled variation of the data
    
    for ij=1:size(REC,2)
        E2=1-sum((ORIG(:,ij)-REC(:,ij)).^2)/sum((ORIG(:,ij)-mean(ORIG(:,ij))).^2);
        E(1,ij)=E2; clear E2
    end
    
    AllVAF(n_mol,1) = mean(E);
    
    subplot(6,6,n_mol)
    plot(ORIG(:,1)); hold on; plot(REC(:,1), 'r')
    title([num2str(n_mol) ' - VAF: ' num2str(E(1))])
    
    nH = ['avr.H'];
    nA = ['avr.A'];
    nE = ['avr.VAF'];
    nR = ['avr.REC'];
    
    eval([nH ' {1,n_mol} = H;'])
    eval([nA ' {1,n_mol} = W;'])
    eval([nE ' {1,n_mol} = E;'])
    eval([nR ' {1,n_mol} = REC;'])
    clear rec; clear W; clear H; clear E; clear nH; clear nA; clear nE; clear nR;
end

plot(AllVAF)
hold on
plot([0 32], [0.9 0.9], '--')
F = find(AllVAF>0.9); F = F(1); % minimum number of synergies to reach reconstruction quality above 90%
plot([F F], [0 1], '-k')
xlabel('number of synergies (features)')
ylabel('VAF')
title(' number of synergies to explain 32-muscle EMG from walking')

%% plotting data with 6 synergies
nSyn = F;
s = [6 5 7 3 4 2 1]; %% sequence of synergies, sorted by the peak timing from activation signals

figure(2)
for a = 1:nSyn
    subplot(nSyn,1,a)
    bar(avr.H{1,nSyn}(s(a),:))
    if a == 7
        xlabel('EMG channels')
    end
end

figure(3)
%% plotting data with 6 synergies
for a = 1:nSyn
    subplot(nSyn,1,a)
    plot(linspace(1,100,1000),avr.A{1,nSyn}(:,s(a)), 'linewidth', 4)
    if a == 7
        xlabel('% gait cycle')
    end
end


