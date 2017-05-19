using Convex, Gurobi, PyPlot

eh=readdlm("datos/e_high.csv")
em=readdlm("datos/e_med.csv")
el=readdlm("datos/e_low.csv")
d=readdlm("datos/demanda.csv")

delta_t = 5/60; #(5 min)
T=collect(5/60:delta_t:24*7)
n=size(T)[1];
T2=[0;T]

#cargo los vectores en kWh (multiplico por delta_t)
d=[d;d;d;d;d;d;d]*delta_t;
e=[eh;em;el;el;em;eh;em]*delta_t;

#Capacidad del Banco
B_max = 308.2;
#Potencia maxima del banco
p_bmax = 36*delta_t;
#Potencia maxima generador
p_dmax = 40*delta_t;
#Potencia maxima solar
p_emax = 52*delta_t;

#Construyo el modelo usando Convex
println("****************************")
println("Building Model")
println("****************************")
#solver=MosekSolver(MSK_DPAR_MIO_TOL_REL_GAP=0.05,LOG=0);
solver=GurobiSolver(MIPGap=0.02);
set_default_solver(solver);

#Defino el modelo
x=Variable(n+1);
y=Variable(n);
u=Variable(n, :Bin);

#Defino el problema
p=minimize(sum(u) + sum(abs(u[2:end]-u[1:end-1])));

#agrego restricciones
#p.constraints += x>=0;						#bateria positiva
p.constraints += x<=B_max;					#capacidad del banco
p.constraints += y>=0;						#generacion solar positiva
p.constraints += u>=0;
p.constraints += u<=1;						#generacion diesel On-OFF
p.constraints += x[2:end]-x[1:end-1] == y+p_dmax*u-d;		#carga de bateria
#p.constraints += x[end] == x[1];		                #bateria final igual a inicial
p.constraints += x[1] == B_max/2;
p.constraints += x>=0.2*B_max;
p.constraints += y<=e;						#y=uso de la energia solar posible
p.constraints += x[2:end]-x[1:end-1]<= p_bmax;			#maxima carga de bateria
p.constraints += x[2:end]-x[1:end-1]>= -p_bmax		   	#maxima descarga de bateria

println("Done")
println("****************************")


#resuelvo
solve!(p)
println("****************************")
println(p.status)

println("Objective value: ", p.optval)
uast = u.value;
yast = y.value;

writedlm("output/u.csv",[T uast]," ")
writedlm("output/e.csv",[T e]," ")
writedlm("output/y.csv",[T yast]," ")
writedlm("output/d.csv",[T d]," ")


xast = x.value
writedlm("output/x.csv",[T2 xast]," ")

plot(T,e)
plot(T,d)
plot(T,p_dmax*uast)
show()
readline()

figure()
plot(T2,xast/B_max)
show()
readline()
