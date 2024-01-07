clear
syms x1 x2 v u1 u2 a ol or omega dT w r lm_i real

x=[x1;x2];
u=[u1;u2];
%10 lidar SLAM landmarks
l1 = sym('l_1_%d',[1 10],'real');
l2 = sym('l_2_%d',[1 10],'real');
lm=reshape([l1;l2],2,10)
l=reshape(lm,20,1);
X=[x;v;u;l];

%%


%prediction equations
R=[0 -1;1 0]; %90 deg rotation
f=X+dT*[v*u;a;omega*R*u;zeros(20,1)];
F=jacobian(f,X);
FNum=matlabFunction(F);


%measurements

%magnetometer
M=[1;0]; %global magnetometer vector
h1=[M'*u;M'*R*u];
H1=jacobian(h1,X);
%%
%wheel odometry
%ol,or are measured wheel angular velocities
%omega = (ol-or)*r/w => omega*w/r = (ol-or)
%v = (ol+or)*r => v/r = (ol+or)
%omega*w/r + v/r = 2*ol => (omega*w + v)/(2*r) = ol
%v/r - omega*w/r = 2*or => (v - omega*w)/(2*r) = or
h2=[(omega*w + v)/(2*r);(v - omega*w)/(2*r)];
H2=jacobian(h2,X);
%%

%lidar SLAM landmark - distance (squared) and angle (cos sin)
H3={};
for k=1:10
    h3=[(lm(:,k)-x).'*(lm(:,k)-x);(lm(:,k)-x)'*u; (lm(:,k)-x)'*R*u];
    J3=jacobian(h3,X);
    J3Num=matlabFunction(J3);
    H3{k}=J3Num;
end





