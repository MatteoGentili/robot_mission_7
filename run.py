from model import Environnement, CommunicationEnvironnement
import seaborn as sns
import argparse
import os

def main(robots_numbers = [3, 3, 3], NbWastes = 16, GridLen = 21, GridHeight = 3):
    
    environnement = CommunicationEnvironnement(robots_numbers, NbWastes, GridLen, GridHeight, False)
    # print(environnement.grid.radioactivity_map.shape)
    # print(len(environnement.grid._grid), len(environnement.grid._grid[0]))
    
    environnement.run_while()
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
    if not os.path.exists("figures"):
        os.makedirs("figures")
    g.figure.savefig("figures/nbwastes_carried.png")
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
    g.figure.savefig("figures/wastes_remaining.png")
    # clear the figure
    g.figure.clear()

    #NbRecycle
    g = sns.lineplot(data=model_vars, x=model_vars.index, y="FullRecycled")
    g.set(
        xlabel="Step",
        ylabel="Number of waste recycled",
        title="Number of waste recycled"
    )
    g.figure.savefig("figures/wastes_fullrecycled.png")
    # clear the figure
    g.figure.clear()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description = 'Choose the parameters for the simulation')

    # Ajoute tous les paramètres de la fonction main
    parser.add_argument('--green_robot', type=int, default=3, help='Number of green robots')
    parser.add_argument('--yellow_robot', type=int, default=3, help='Number of yellow robots')
    parser.add_argument('--red_robot', type=int, default=3, help='Number of red robots')
    parser.add_argument('--NbWastes', type=int, default=16, help='Number of wastes')
    parser.add_argument('--GridLen', type=int, default=21, help='Grid length')
    parser.add_argument('--GridHeight', type=int, default=3, help='Grid height')

    # Run la fonction main avec ces paramètres
    args = parser.parse_args()
    main([args.green_robot, args.yellow_robot, args.red_robot], args.NbWastes, args.GridLen, args.GridHeight)

