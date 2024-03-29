from model import Environnement
import seaborn as sns

def main(nsteps=1):
    robots_numbers = [3, 3, 3]
    environnement = Environnement(robots_numbers, 10, 15, 3, True)
    print(environnement.grid.radioactivity_map.shape)
    print(len(environnement.grid._grid), len(environnement.grid._grid[0]))
    environnement.run_n_steps(nsteps)
    # environnement.grid.print()
    environnement.grid.draw()
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
    g.figure.savefig("output.png")

if __name__ == "__main__":
    main(100)