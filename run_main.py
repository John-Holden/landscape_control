import os
import numpy as np

PATH_TO_DATA_STORE = f'{os.getcwd()}/data_store'

class Ensemble_info():   # High level struct, holds all ensemble info
    def __init__(self, ensemble_name :str):
        self.species = 'fex'
        self.beta_index = 0  # choose index of
        self.path_to_ensemble = f'{PATH_TO_DATA_STORE}/{ensemble_name}'
        self.R0_vs_rho_beta = np.load(f'{self.path_to_ensemble}/ensemble.npy')
        self.rhos = np.load(f'{self.path_to_ensemble}/rhos.npy')
        self.betas = np.load(f'{self.path_to_ensemble}/betas.npy')
        # x 0.01 ==> Covert to canopy cover density
        self.raw_data = 0.01 * np.genfromtxt(f'{PATH_TO_DATA_STORE}/{self.species}.csv', delimiter=',')
        # Clean channel isles etc.
        self.raw_data = self.raw_data * np.load(f'{PATH_TO_DATA_STORE}/uk_isle_shape.npy')[1:-1, 1:-1]


def orchestrate_main(ensemble_name):  # import & run delegator methods
    from delegator_methods import get_single_R0_cluster_map, fragment_R0_map

    coarse_grain_factor = 5

    R0_out = get_single_R0_cluster_map(ensemble_name=ensemble_name, coarse_grain_factor=coarse_grain_factor,
                                       beta_index=1)

    fragment_R0_map(alpha_steps='auto', R0_map_raw=R0_out, fragmentation_iterations=5)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ensembles = {0: 'landscape_control_input_test_data',
                 1: 'landscape_control_input_test_beta_cluster_sizes'}


    orchestrate_main(ensemble_name=ensembles[0])



