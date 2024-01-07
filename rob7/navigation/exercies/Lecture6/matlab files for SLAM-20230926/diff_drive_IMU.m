function [x,u,v] = diff_drive_IMU(x,u,v,omega,a,dT)
 x=x+dT*u*v;
 v=v+dT*a;
 u=u+dT*[0 -1;1 0]*u*omega;
 u=u/norm(u); %renormalization of u
end

