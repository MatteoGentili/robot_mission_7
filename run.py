from model import Environnement
import seaborn as sns

def main(nsteps=1):
    robots_numbers = [3, 3, 3]
    environnement = Environnement(robots_numbers, 5, 10, 3, True)
    environnement.run_n_steps(nsteps)
    environnement.grid.print()
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


if __name__ == "__main__":
    main(500)