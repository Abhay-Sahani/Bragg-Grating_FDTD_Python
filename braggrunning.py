import os, sys

dll_dir = r"C:\Program Files\Lumerical\v202\api\python"

if hasattr(os, "add_dll_directory"):
    os.add_dll_directory(dll_dir)
else:
    # Python < 3.8 fallback
    os.environ["PATH"] = dll_dir + os.pathsep + os.environ.get("PATH", "")

import lumapi

import numpy as np

def create_and_run():
    fdtd = lumapi.FDTD()

    # Parameters
    thick_Si = 0.22e-6
    thick_BOX = 2e-6
    width_ridge = 0.5e-6
    Delta_W = 50e-9
    L_pd = 324e-9
    N_gt = 280
    L_gt = N_gt * L_pd
    L_ex = 5e-6
    lambda_min = 1.5e-6
    lambda_max = 1.6e-6
    freq_points = 101
    sim_time = 6000e-15
    Mesh_level = 2
    dx = 40.5e-9; dy = 50e-9; dz = 20e-9

    mat_Si = "Si (Silicon) - Palik"
    mat_BOX = "SiO2 (Glass) - Palik"

    # Substrate
    fdtd.addrect(name="oxide", x_min=-L_ex, x_max=L_gt+L_ex,
                 y=0, y_span=3e-6,
                 z_min=-thick_BOX, z_max=-thick_Si/2,
                 material=mat_BOX)
    # Input WG
    fdtd.addrect(name="input_wg", x_min=-L_ex, x_max=0,
                 y=0, y_span=width_ridge,
                 z=0, z_span=thick_Si, material=mat_Si)
    # Bragg grating cell
    fdtd.addrect(name="grt_big", x_min=0, x_max=L_pd/2,
                 y=0, y_span=width_ridge+Delta_W,
                 z=0, z_span=thick_Si, material=mat_Si)
    fdtd.addrect(name="grt_small", x_min=L_pd/2, x_max=L_pd,
                 y=0, y_span=width_ridge-Delta_W,
                 z=0, z_span=thick_Si, material=mat_Si)
    fdtd.selectpartial("grt")
    fdtd.addtogroup("grt_cell")
    fdtd.select("grt_cell")
    fdtd.redrawoff()
    for _ in range(N_gt-1):
        fdtd.copy(L_pd)
    fdtd.selectpartial("grt_cell")
    fdtd.addtogroup("bragg")
    fdtd.redrawon()
    # Output WG
    fdtd.addrect(name="output_wg", x_min=L_gt, x_max=L_gt+L_ex,
                 y=0, y_span=width_ridge,
                 z=0, z_span=thick_Si, material=mat_Si)

    # FDTD setup
    fdtd.addfdtd()
    fdtd.set("dimension", "3D")
    fdtd.set("simulation time", sim_time)
    fdtd.set("x min", -L_ex+1e-6); fdtd.set("x max", L_gt+L_ex-1e-6)
    fdtd.set("y", 0); fdtd.set("y span", 2e-6)
    fdtd.set("z", 0); fdtd.set("z span", 1.8e-6)
    fdtd.set("mesh accuracy", Mesh_level)
    for b in ["x min bc","x max bc","y min bc","y max bc","z min bc","z max bc"]:
        fdtd.set(b, "PML")

    # Mesh override
    fdtd.addmesh()
    fdtd.set("x min",0); fdtd.set("x max", L_gt)
    fdtd.set("y",0); fdtd.set("y span", width_ridge+Delta_W)
    fdtd.set("z",0); fdtd.set("z span", thick_Si+2*dz)
    fdtd.set("dx", dx); fdtd.set("dy", dy); fdtd.set("dz", dz)

    # Mode source
    fdtd.addmode()
    fdtd.set("injection axis","x-axis")
    fdtd.set("mode selection","fundamental mode")
    fdtd.set("x",-2e-6)
    fdtd.set("y",0); fdtd.set("y span",2.5e-6)
    fdtd.set("z",0); fdtd.set("z span",2e-6)
    fdtd.set("wavelength start", lambda_min)
    fdtd.set("wavelength stop", lambda_max)

    # Monitors
    fdtd.addtime(name="tmonitor_r", monitor_type="point", x=-3e-6, y=0, z=0)
    fdtd.addtime(name="tmonitor_m", monitor_type="point", x=L_gt/2, y=0, z=0)
    fdtd.addtime(name="tmonitor_t", monitor_type="point", x=L_gt+3e-6, y=0, z=0)
    fdtd.addpower(name="t", monitor_type="2D X-normal", x=L_gt+2.5e-6,
                  y=0, y_span=2.5e-6, z=0, z_span=2e-6,
                  override_global_monitor_settings=1,
                  use_source_limits=1,
                  use_wavelength_spacing=1,
                  frequency_points=freq_points)
    fdtd.addpower(name="r", monitor_type="2D X-normal",
                  x=-2.5e-6, y=0, y_span=2.5e-6, z=0, z_span=2e-6,
                  override_global_monitor_settings=1,
                  use_source_limits=1,
                  use_wavelength_spacing=1,
                  frequency_points=freq_points)

    fdtd.save("Bragg_FDTD")
    fdtd.run()

    # Analysis
    t = fdtd.getresult("t", "T")
    r = fdtd.getresult("r", "T")
    f = t["f"]
    lam = 3e8/f
    T = t["T"]
    R = r["T"]

    return lam*1e9, 10*np.log10(T), 10*np.log10(R)

if __name__=="__main__":
    lam, T_db, R_db = create_and_run()
    for w, t, r in zip(lam[::10], T_db[::10], R_db[::10]):
        print(f"{w:.2f} nm | T = {t:.2f} dB | R = {r:.2f} dB")
