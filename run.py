from model import Environnement, CommunicationEnvironnement, RandomEnvironnement
import seaborn as sns
import argparse
import os
    

def main(robots_numbers = [3, 3, 3], NbWastes = 16, GridLen = 21, GridHeight = 3, OPTI = False, debug = False):
    if not os.path.exists("figures"):
        os.makedirs("figures")
    if OPTI:
        environnement = CommunicationEnvironnement(robots_numbers, NbWastes, GridLen, GridHeight, debug)
        # environnement = Environnement(robots_numbers, NbWastes, GridLen, GridHeight, False)
        # print(environnement.grid.radioactivity_map.shape)
        # print(len(environnement.grid._grid), len(environnement.grid._grid[0]))
        
        environnement.run_while()
        # environnement.grid.print()
        # environnement.grid.draw()
        # environnement.master.mainloop()
        agent_inventory = environnement.datacollector.get_agent_vars_dataframe()
        last_step = agent_inventory.index.get_level_values('Step').max()
        agent_inventory = agent_inventory.xs(last_step, level="Step")["Carry"]
        print("Opti : ", last_step)
        model_vars = environnement.datacollector.get_model_vars_dataframe()
        print("MODEL vars column : ", model_vars.columns)
        # Number of messages sent
        for colour in ["green", "yellow", "red"] :
            g = sns.lineplot(data=model_vars, x=model_vars.index, y="NbMessages_"+colour, color = colour)
            g.set(
                xlabel="Step",
                ylabel=f"Number of messages sent",
                title="Number of messages sent"
            )
        g.figure.savefig("figures/nbmessages_sent.png")
        # clear the figure
        g.figure.clear()
    
    else:
        # environnement = CommunicationEnvironnement(robots_numbers, NbWastes, GridLen, GridHeight, False)
        # environnement = Environnement(robots_numbers, NbWastes, GridLen, GridHeight, debug)
        environnement = RandomEnvironnement(robots_numbers, NbWastes, GridLen, GridHeight, debug)
        # print(environnement.grid.radioactivity_map.shape)
        # print(len(environnement.grid._grid), len(environnement.grid._grid[0]))
        
        environnement.run_while()
        # environnement.grid.print()
        # environnement.grid.draw()
        # environnement.master.mainloop()
        agent_inventory = environnement.datacollector.get_agent_vars_dataframe()
        last_step = agent_inventory.index.get_level_values('Step').max()
        agent_inventory = agent_inventory.xs(last_step, level="Step")["Carry"]
        print("Non Opti : ", last_step)
        model_vars = environnement.datacollector.get_model_vars_dataframe()
        print("MODEL vars column : ", model_vars.columns)


    # Number of waste carried by each robot
    g = sns.histplot(agent_inventory, discrete=True)
    g.set(
        xlabel="Number of waste carried",
        ylabel="Number of robots",
        title="Number of waste carried by each robot"
    )
    g.figure.savefig("figures/nbwastes_carried_nonopti.png") if not OPTI else g.figure.savefig("figures/nbwastes_carried_opti.png")
    # clear the figure
    g.figure.clear()

    #NbRecycle
    g = sns.lineplot(data=model_vars, x=model_vars.index, y="FullRecycled")
    g.set(
        xlabel="Step",
        ylabel="Number of waste recycled",
        title="Number of waste recycled"
    )
    g.figure.savefig("figures/wastes_fullrecycled_nonopti.png") if not OPTI else g.figure.savefig("figures/wastes_fullrecycled_opti.png")
    # clear the figure
    g.figure.clear()


    # NbWaste
    for colour in ["green", "yellow", "red"] :
        g = sns.lineplot(data=model_vars, x=model_vars.index, y=colour, color = colour)
        g.set(
            xlabel="Step",
            ylabel=f"Number of wastes remaining in the grid",
            title="Number of waste remaining in the grid"
        )
    g.figure.savefig(f"figures/wastes_remaining_opti.png") if OPTI else g.figure.savefig(f"figures/wastes_remaining_nonopti.png")
    # clear the figure
    g.figure.clear()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description = 'Choose the parameters for the simulation')

    # Ajoute tous les paramètres de la fonction main
    parser.add_argument('--green_robot', type=int, default=5, help='Number of green robots')
    parser.add_argument('--yellow_robot', type=int, default=3, help='Number of yellow robots')
    parser.add_argument('--red_robot', type=int, default=3, help='Number of red robots')
    parser.add_argument('--nb_wastes', type=int, default=16, help='Number of wastes')
    parser.add_argument('--grid_width', type=int, default=21, help='Grid length')
    parser.add_argument('--grid_height', type=int, default=3, help='Grid height')
    parser.add_argument('--opti', type=str, default="True", help='Optimised version')
    parser.add_argument('--debug', type=str, default="False", help='Debug mode')
    # Run la fonction main avec ces paramètres
    args = parser.parse_args()
    opti = True if args.opti.lower() == "true" else False
    debug = True if args.debug.lower() == "true" else False
    main([args.green_robot, args.yellow_robot, args.red_robot], args.nb_wastes, args.grid_width, args.grid_height, opti, debug)

