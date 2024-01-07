clear
diff_drive_IMU_sym_SLAM
R90=[0 -1;1 0];
T=100; %simulation time
dT=0.1; %simulation time step
N=ceil(T/dT);
x=zeros(2,N); %positions
x(:,1)=[0;-5];
u=x; %headings
v=zeros(1,N); %forward velocities
v(1)=1;
u(:,1)=[1;0];

%landmark positions
th=(0:4)*2*pi/5;
%inner circle
l_inner=3*[cos(th+pi/2);sin(th+pi/2)];
%outer circle
l_outer=7*[cos(th-pi/2);sin(th-pi/2)];
lm=[l_inner l_outer];

%recorded landmarks
lm_found=[1e6;1e6]; %initial dummy

%estimated state
X_est=zeros(2+1+2+2*10,N); %x,v,u,l X 10
X_est(1:2,1)=x(:,1);
X_est(3,1)=v(1);
X_est(4:5,1)=u(:,1);

%Noise covariances
Q=diag(0.2*[ones(1,2+1+2) 0*ones(1,2*10)]);
Rl=eye(3);
P=eye(2+1+2+2*10);
P(1:7,1:7)=zeros(7,7);


for i=1:N-1
    a=0;
    omega=1/5;
    %Simulation time step
    rrand=randn(1)*0.2;
    [X,U,V]=diff_drive_IMU(x(:,i),u(:,i),v(i),omega+rrand,a,dT);
    x(:,i+1)=X;
    u(:,i+1)=U;
    v(i+1)=V;
    
    %state prediction for robot states
    [X_pred,U_pred,V_pred]=diff_drive_IMU(X_est(1:2,i),X_est(4:5,i),X_est(3,i),omega,a,dT);
    X_est(1:2,i+1)=X_pred;
    X_est(4:5,i+1)=U_pred;
    X_est(3,i+1)=V_pred;
    %prediction of landmarks - constant predictor
    X_est(2+1+2+1:end,i+1)=X_est(2+1+2+1:end,i);
    
    %compute distances to landmarks
    diff=x(:,i)*ones(1,10)-lm;
    dist=diff(1,:).^2+diff(2,:).^2;
    I=find(dist<3^2);
    
    %determine positions of landmarks in sight
    %find angle and distance
    clear lm_loc
    for k=1:length(I)
        d=norm(x(:,i)-lm(:,I(k))); 
        d_est=norm(X_est(1:2,i)-lm(:,I(k)));
        uu1=(lm(:,I(k))-x(:,i))'*u(:,i)/d;
        uu2=(lm(:,I(k))-x(:,i))'*(R90*u(:,i))/d;
        lm_loc(:,k)=d*(uu1*X_est(4:5,i)+uu2*R90*X_est(4:5,i))+X_est(1:2,i); %estimated landmark position in global coordinates
        y_meas=[d^2;uu1;uu2];
        
        %compute distances to found landmarks - should be from X_est
        diff=lm_loc(:,k)*ones(1,length(lm_found))-lm_found;
        dist=diff(1,:).^2+diff(2,:).^2;
        [HH II]=min(dist);
        %HH
        if(HH>1.2^2) %new landmark detected
            lm_found=[lm_found lm_loc(:,k)]; %insert newly found landmark
            lm_index=2+1+2+2*(size(lm_found,2)-1)-1;
            %insert landmark in estimated state vector
            X_est(lm_index:lm_index+1,i+1)=lm_loc(:,k);
            
        elseif(d_est>0.2)%old landmark revisited
            %use landmark for EKF
            %disp('correction')
            %compute EKF matrices
            clear F
            F=FNum(dT,omega,X_est(4,i+1),X_est(5,i+1),X_est(3,i+1));
            lm_index=2+1+2+2*(II-1)-1;
            H=H3{II-1}(lm_found(1,II),lm_found(2,II),X_est(4,i+1),X_est(5,i+1),X_est(1,i+1),X_est(2,i+1));
            %compute predicted measurement
            d_pred=norm(X_est(1:2,i+1)-X_est(lm_index:lm_index+1,i+1));
            uu1_pred=(X_est(lm_index:lm_index+1,i+1)-X_est(1:2,i+1))'*X_est(4:5,i+1)/d;
            uu2_pred=(X_est(lm_index:lm_index+1,i+1)-X_est(1:2,i+1))'*(R90*X_est(4:5,i+1))/d;
            y_pred=[d_pred^2;uu1_pred;uu2_pred]; %predicted output
            
            %EKF correction equations
            P=F*P*F'+Q; %residual covariance
            S=H*P*H'+Rl;
            K=P*H'*inv(S);
            %y_meas-y_pred
            X_est(:,i+1)=X_est(:,i+1)+K*(y_meas-y_pred);
            P=(eye(2+1+2+2*10)-K*H)*P;
            figure(2)
            mesh(P(6:end,6:end))
        end
    end
    
    
    figure(1)
    clf
    plot(x(1,i),x(2,i),'r*')
    hold on
    plot([x(1,i) x(1,i)+u(1,i)],[x(2,i) x(2,i)+u(2,i)])
    plot(X_est(1,i),X_est(2,i),'ro')
    plot([X_est(1,i) X_est(1,i)+X_est(4,i)],[X_est(2,i) X_est(2,i)+X_est(5,i)])
    plot(lm(1,:),lm(2,:),'b*')
    plot(lm(1,I),lm(2,I),'g*')
    plot(lm_found(1,2:end),lm_found(2,2:end),'go')
    pause(0.01)
    i
end
plot(x(1,:),x(2,:),lm(1,:),lm(2,:),'*')
hold on
plot(X_est(1,:),X_est(2,:),'.')
l_est=X_est(2+1+2+1:end,i);
plot(l_est(1:2:end-1),l_est(2:2:end),'bo')
