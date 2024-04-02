from model import Environnement
import seaborn as sns

def main(nsteps=1):
    robots_numbers = [3, 3, 3]
    NbWastes = 10
    GridLen = 15
    GridHeight = 3
    environnement = Environnement(robots_numbers, NbWastes, GridLen, GridHeight, False)
    # print(environnement.grid.radioactivity_map.shape)
    # print(len(environnement.grid._grid), len(environnement.grid._grid[0]))
    
    environnement.run_n_steps(nsteps)
    # environnement.grid.print()
    # environnement.grid.draw()
    environnement.master.mainloop()
    agent_inventory = environnement.datacollector.get_agent_vars_dataframe()
    last_step = agent_inventory.index.get_level_values('Step').max()
    agent_inventory = agent_inventory.xs(last_step, level="Step")["Carry"]
    g = sns.histplot(agent_inventory, discrete=True)
    g.set(
        xlabel="Number of waste carried",
        ylabel="Number of robots",
        title="Number of waste carried by each robot"
    )
    g.figure.savefig("nbwastes_carried.png")
    # clear the figure
    g.figure.clear()

    #NbWaste
    model_vars = environnement.datacollector.get_model_vars_dataframe()
    print(model_vars.columns)
    # NbWaste = model_vars["NbWaste"]
    g = sns.lineplot(data=model_vars, x=model_vars.index, y="NbWaste")
    g.set(
        xlabel="Step",
        ylabel="Number of wastes remaining in the grid",
        title="Number of waste remaining in the grid"
    )
    g.figure.savefig("wastes_remaining.png")
    # clear the figure
    g.figure.clear()

    #NbRecycle
    g = sns.lineplot(data=model_vars, x=model_vars.index, y="FullRecycled")
    g.set(
        xlabel="Step",
        ylabel="Number of waste recycled",
        title="Number of waste recycled"
    )
    g.figure.savefig("wastes_fullrecycled.png")
    # clear the figure
    g.figure.clear()

if __name__ == "__main__":
    main(500)