X = mean(S1_EMGflt(:,1:16,:),3);
% N = 1000
% M = 16

%% Running Non-negative Matrix Factorizations
[W, H] = nnmf(X,1) % K = number of features to be tested (1 to 16)

% Reconstruction
REC1 = W*H;

%% NNMF with 5 features (synergies)
[W, H] = nnmf(X,5) % K = number of features to be tested (1 to 16)

% Reconstruction
REC2 = W*H;

%% Plots
clf; %Clear the figure
plot(X(:,1), 'Color','k', 'LineWidth',3)
hold on
plot(REC1(:,1), 'Color','r', 'LineWidth',3)
plot(REC2(:,1), 'Color','g', 'LineWidth',3)
legend('Original', 'REC 1 synergy', 'REC 5 synergies')


%% Calculation of Variablity Accounted For (VAF) for each muscle

% VAF = 1 l SSE/SST, (Sum of Squared Errors)/(Total Sum of Square) 
% where SSE is the unexplained variation and 
% SST is the pooled variation of data

i = 1; % VAF for muscle i. 
VAF1 = 1 - sum((X(:,i) - REC1(:,i)).^2)/sum((X(:,i) - mean(X(:,i))).^2);

for i = 1:size(REC2,2)
    VAF2(1,i) = 1 - sum((X(:,i) - REC2(:,i)).^2)/sum((X(:,i) - mean(X(:,i))).^2);
end

clf;
figure
bar(VAF2)

