%demonstrating iterative solution of MDP problem from slides
clear
%
% The discounting factor lambda
lambda=0.9;
mmax=1e4;
%Reward matrix with edges
R=1e6*ones(5,6);
R(2:4,2:5)=-0.04*ones(3,4);
R(3,3)=1e6;
R(2,5)=0.1;
R(3,5)=-1;

%U=zeros(5,6); %initial utility
U=-0*1e6*ones(5,6); %initial utility
U(2:4,2:5)=zeros(3,4);
Un=U;

% In the format of [x,y, R(s)] 
Tleft=[0 -1 0.8;-1 0 0.1;1 0 0.1];
Tright=[0 1 0.8;-1 0 0.1;1 0 0.1];
Tup=[-1 0 0.8;0 -1 0.1; 1 0 0.1];
Tdown=[1 0 0.8; 0 -1 0.1; 0 1 0.1];

% Number of itterations
Nit=20;

% Itterate through all indecies in the cell environment. 
for it=1:Nit
    for i=2:4
        for j=2:5
            max=-1e7;
            %left
            s=0;
            P=0;
            for k=1:3
                if(R(i+Tleft(k,1),j+Tleft(k,2))<mmax)
                    s=s+U(i+Tleft(k,1),j+Tleft(k,2))*Tleft(k,3);
                    P=P+Tleft(k,3);    
                end
            end
            if(R(i,j)+lambda*s/P>max && R(i+Tleft(1,1),j+Tleft(1,2))<mmax)
                max=R(i,j)+lambda/P*s;
                Policy{i,j}='left';
            end
            %right
            s=0;
            P=0;
            for k=1:3
                if(R(i+Tright(k,1),j+Tright(k,2))<mmax)
                    s=s+U(i+Tright(k,1),j+Tright(k,2))*Tright(k,3);
                    P=P+Tright(k,3);
                end
            end
            if(R(i,j)+lambda*s/P>max && R(i+Tright(1,1),j+Tright(1,2))<mmax)
                max=R(i,j)+lambda/P*s;
                Policy{i,j}='right';
            end
            %up
            s=0;
            P=0;
            for k=1:3
                if(R(i+Tup(k,1),j+Tup(k,2))<mmax)
                    s=s+U(i+Tup(k,1),j+Tup(k,2))*Tup(k,3);
                    P=P+Tup(k,3);
                end
            end
            if(R(i,j)+lambda*s/P>max && R(i+Tup(1,1),j+Tup(1,2))<mmax)
                max=R(i,j)+lambda*s/P;
                Policy{i,j}='up';
            end
            %down
            s=0;
            P=0;
            for k=1:3
                if(R(i+Tdown(k,1),j+Tdown(k,2))<mmax)
                s=s+U(i+Tdown(k,1),j+Tdown(k,2))*Tdown(k,3);
                P=P+Tdown(k,3);
                end
            end
            if(R(i,j)+lambda*s/P>max && R(i+Tdown(1,1),j+Tdown(1,2))<mmax)
                max=R(i,j)+lambda*s/P;
                Policy{i,j}='down';
            end

            Un(i,j)=max;
            Un(3,5)=lambda*Un(3,5)+R(3,5);
            Un(2,5)=lambda*Un(2,5)+R(2,5);
            Policy{2,5}='idle';
        end
    end
    U=Un;
end

disp(U.*(U<mmax))