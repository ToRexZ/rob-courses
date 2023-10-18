C=ones(22,22)*1e2;
C(2:21,2:21)=zeros(20,20);
Cold=C;

for it=1:50
    for i=2:21
        for j=2:21
            C(i,j)=1+min([Cold(i+1,j) Cold(i-1,j) Cold(i,j-1) Cold(i,j+1)]);
            m(i,j) = abs(i-10) + abs(j-10);
            C(10,10)=0;
        end
        Cold=C;
    end
    figure(1)
    mesh(C(2:21,2:21))
    
end
figure(2)
mesh(m(2:21,2:21))
figure(3)
mesh(m(2:21,2:21)+C(2:21,2:21))