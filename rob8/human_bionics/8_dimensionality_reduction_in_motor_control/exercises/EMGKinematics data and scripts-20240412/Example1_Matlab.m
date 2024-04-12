
X = mean(S1_EMGflt(:,1:16,:),3); % data reduced to average, from first 16 channels
% N = 1000
% M = 16
%% running NMF for 1 feature (synergy)
[W,H] = nnmf(X,1); % K = number of features to be tested (1 to 16)
REC1 = W*H;

%% running NMF for 5 features (synergies)
[W,H] = nnmf(X,5); % K = number of features to be tested (1 to 16)
REC2 = W*H;

%% making plots
plot(X(:,1), 'Color', 'k', 'linewidth', 3)
hold on
plot(REC1(:,1), 'Color', 'r', 'linewidth', 3)
plot(REC2(:,1), 'Color', 'g', 'linewidth', 3)
legend('ORIGINAL', 'REC 1 synergy', 'REC 5 synergies')


%% calculating VAF for each muscle
% VAF = 1 ? SSE/SST, where  SSE(sum of squared errors)is the unexplained variation
%                           SST(total sum of squares) is the pooled variation of the data

i = 1; % muscle to calculate VAF (Variability Accounted For)
VAF1 = 1 - sum((X(:,i)-REC1(:,i)).^2)/sum((X(:,i)-mean(X(:,i))).^2);

for i = 1:size(REC2,2)
    VAF2(1,i) = 1 - sum((X(:,i)-REC2(:,i)).^2)/sum((X(:,i)-mean(X(:,i))).^2);
end





