import pprint
import warnings
import numpy as np
import matplotlib
from typing import Optional
import matplotlib.pyplot as plt
from typing import Union, Iterable
from matplotlib.colors import LinearSegmentedColormap

from ._cluster_find import rank_cluster_map
from parameters_and_setup import PATH_TO_INPUT_DATA
from landscape_control.exceptions import NoClustersDetcted

pltParams = {'figure.figsize': (9., 6.5),
             'axes.labelsize': 15,
             'ytick.labelsize': 15,
             'xtick.labelsize': 15,
             'legend.fontsize': 'x-large'}

plt.rcParams.update(pltParams)


def plot_R0_vs_rho_over_ensemble(ensemble_name):
    """ Plot R0 vs Rho for beta values """
    from .domain_processing import linear_func
    from scipy.optimize import curve_fit

    path_to_ensemble = f'{PATH_TO_INPUT_DATA}/{ensemble_name}'

    R0_vs_rho_ensemble = np.load(f'{path_to_ensemble}/ensemble.npy')
    rhos = np.load(f'{path_to_ensemble}/rhos.npy')
    betas = np.load(f'{path_to_ensemble}/betas.npy')
    for i, R0_vs_rho in enumerate(R0_vs_rho_ensemble):
        plt.plot(rhos, R0_vs_rho, label=f'Betas : {betas[i]}', c=f'C{i}')
        plt.scatter(rhos, R0_vs_rho, c=f'C{i}')
        popt, pcov = curve_fit(linear_func, rhos, R0_vs_rho)
        print(f'BETA: {betas[i]} | P out = {popt[0]}, Variance = {pcov[0]}')
        plt.plot(rhos, rhos * popt[0], ls='--',
                 label=f'fitted {round(popt[0])}', c=f'C{i}')

    plt.plot([rhos[0], rhos[-1]], [1, 1], c='r', ls='--')
    plt.show()
    return


def plot_cluster_sizes_vs_beta(betas: Iterable, cluster_sizes: Iterable, cluster_rank: int = 1, save: bool = False):
    """
    Plot how top cluster size varies with infectivity beta.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    if type(cluster_sizes) == np.ndarray:
        betas = [betas]
        cluster_sizes = [cluster_sizes]
    labels = ['Gaussian', 'power law']
    for i in range(len(cluster_sizes)):
        ax.plot(betas[i], cluster_sizes[i], label=f'{labels[i]}')
        ax.scatter(betas[i], cluster_sizes[i])

    plt.xticks(rotation=15)
    plt.xlabel(r'$\beta$')
    plt.gcf().subplots_adjust(bottom=0.15)
    plt.ylabel(f"Rank {cluster_rank} cluster size km^2")
    plt.legend()
    plt.yscale('log')
    if save:
        plt.savefig('cluster_sz_vs_beta.pdf', bbox_inches='tight')
    plt.show()


def plot_cluster_size_comparison_over_beta(cluster_sz_dat: list, beta_dat:list, cluster_rank: int = 1,
                                           save: Optional[bool] = None):
    """
    Plot a comparison of cluster-size over beta for power-law vs gaussian
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    for cluster_sz, betas in zip(cluster_sz_dat, beta_dat):
        ax.plot(betas, cluster_sz)
        ax.scatter(betas, cluster_sz)

    plt.ylabel(rf"Rank {cluster_rank} cluster size $km^{2}$")
    plt.xlabel(r'$\beta$')
    if save:
        plt.savefig('cluster_size_ga_pl_comp.pdf')
    plt.show()

def plot_cluster_size_vs_alpha(iteration: int, alpha_steps: Union[list, np.ndarray],
                               largest_cluster_size_vs_alpha: np.ndarray,
                               discontinuity_index: Union[int, None] = None):
    """
    Plot cluster sizes for one iteration and one value of alpha.
    """
    plt.title(f'cluster sizes & index | iteration {iteration}')
    plt.plot(alpha_steps, largest_cluster_size_vs_alpha)
    plt.scatter(alpha_steps, largest_cluster_size_vs_alpha)
    if discontinuity_index is not None:
        plt.plot([alpha_steps[discontinuity_index - 1], alpha_steps[discontinuity_index - 1]],
                 [0, largest_cluster_size_vs_alpha[discontinuity_index - 1]])
    plt.show()
    return


def plot_R0_clusters(R0_map: np.ndarray, rank: Union[None, int] = None, epi_c: Union[None, tuple] = None,
                     show: bool = True, save: bool = False, save_name: Union[None, str] = None, ext: str = '.png',
                     title: str = "", flash: bool = False):
    """
    Rank and plot clusters
    """
    # _, R0_map_background = None, None
    if isinstance(rank, int):
        R0_map_background = np.array(R0_map > 0).astype(int)
        R0_map, _, _ = rank_cluster_map(R0_map, get_ranks=rank)
        R0_map_background = np.array(R0_map > 0).astype(int) - R0_map_background

        if len(_) >= rank:
            cluster_number = rank

        elif rank > len(_) > 0:
            msg = f'\nError, expected {rank} clusters, only found {len(_)}'
            warnings.warn(msg)
            cluster_number = len(_)
        else:
            raise NoClustersDetcted

    colors = [f'C{i}' for i in range(len(np.unique(R0_map)) - 1)]

    if rank is not None and isinstance(rank, int):  # Plot back-ground as grey
        R0_map = R0_map + R0_map_background
        colors.insert(0, 'lightgrey')
        colors.insert(1, 'white')
        nbins = cluster_number + 2
    else:  # Fix me...
        raise NotImplementedError

    cmap_name = 'my_list'
    cm = LinearSegmentedColormap.from_list(cmap_name, colors, N=nbins)
    im = plt.imshow(R0_map, cmap=cm, interpolation='nearest')
    plt.colorbar(im)
    plt.title(title)
    plt.xticks([])
    plt.yticks([])

    if flash:
        matplotlib.rc('axes', edgecolor='r')
    if not flash:
        matplotlib.rc('axes', edgecolor='black')

    if epi_c is not None:
        circle = plt.Circle((epi_c[1], epi_c[0]), 1.5, fc='black', ec="red")
        plt.gca().add_patch(circle)

    if save:
        name = 'cluster_fig' if save_name is None else save_name
        name = f'{name}.{ext}'
        plt.savefig(name)

    if show:
        plt.show()

    plt.close()


def plot_R0_map(R0_map: np.ndarray, save: bool = False, title: str = '', ext: str = 'pdf',
                save_name : Union[None, str] = None):
    """
    Plot a raw R0-valued map, without clustering.
    :param R0_map:
    :return:
    """

    im = plt.imshow(np.where(R0_map<1, np.nan, R0_map), interpolation='nearest')
    plt.colorbar(im)
    plt.xticks([])
    plt.yticks([])
    plt.title(title)
    if save:
        name = save_name if save_name else 'R0-map'
        plt.savefig(f'{name}.{ext}')
    plt.show()
    plt.close()



def plot_fragmented_domain(fragmented_domain: np.ndarray, R0_map: np.ndarray, epi_c: Union[None, tuple] = None,
                           show_text: bool = False):
    """
    `Plot the domain after it has been fragmented
    :param fragmented_domain: a spatial map of identified patche
    :param R0_map: a spatial map of the  domain
    :param epi_c: optional, plot the epicenter when finding payoffs
    :param show_text: optional, show the fragmentation id alongside the containment scenairo.
    """

    frag_number = np.unique(fragmented_domain)
    frag_number = frag_number[1:] if 0 in frag_number else frag_number
    colors = [f'C{i}' for i, line in enumerate(frag_number)]
    colors.insert(0, 'white')
    colors.insert(1, 'lightgrey')

    nbins = len(colors)
    cmap_name = 'my_list'
    cm = LinearSegmentedColormap.from_list(cmap_name, colors, N=nbins)

    # Color fragmentation lines from C0
    show_text_dict = {} if show_text else None
    fragmented_domain_ = np.zeros_like(fragmented_domain)
    for i, frag_line in enumerate(frag_number):
        fragmented_domain_[np.where(fragmented_domain == frag_line)] = i + 2
        if show_text:
            show_text_dict[frag_line] = i + 2

    # Include background of R0 map having numerical value 1 shown as light-grey
    R0_map[np.where(fragmented_domain)] = 0
    fragmented_domain_ += np.where(R0_map > 1, 1, 0)

    im = plt.imshow(fragmented_domain_, cmap=cm)
    plt.colorbar(im)

    # Optional, show epicenter
    if epi_c is not None:
        circle = plt.Circle((epi_c[1], epi_c[0]), 0.5, fc='black', ec="red")
        plt.gca().add_patch(circle)

    # Optional, display fragmentation iteration next to spatial line
    if show_text:
        for frag_line, numerical_val in show_text_dict.items():
            line_ind = np.where(fragmented_domain_ == numerical_val)
            N_points = len(line_ind[0])
            x, y = line_ind[0].sum() / N_points, line_ind[1].sum() / N_points
            plt.text(y, x, f'{frag_line}', c='b', size=10)

    plt.show()
    return


def plot_payoffs_over_beta(payoff: np.ndarray, betas: np.ndarray, max_beta_index: Optional[int] = None,
                           save: Optional[bool] = None):
    """
    Plot the payoff metrics Ns / (Nc * Nr) over the parameter-space of beta
    :param payoff:
    :param betas:
    :param max_beta_index:
    :return:
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    betas = betas[:max_beta_index] if max_beta_index else betas
    payoff = payoff[:max_beta_index] if max_beta_index else payoff
    for i, result in enumerate(payoff):
        ax.scatter([betas[i]]*payoff.shape[1], result, marker='x')
        ax.plot([betas[i]]*payoff.shape[1], result)


    ax.plot(betas, payoff[:, -1], ls='--', c='black', alpha=0.75)
    plt.xticks(rotation=15)
    if save:
        plt.savefig('payoff_over_beta.pdf')
    plt.show()



def process_payoffs(payoff_store: dict, plot: bool = False, title: Optional[str] = None):
    """
    Descend into payoff dictionary and return a sorted array of payoff, number_saved, number_removed and number_culled.
    """
    N_saved = []
    N_culled = []
    N_removed = []

    for epic, payoffs in payoff_store.items():
        # Iterate through epicenters
        for comb, result in payoffs.items():
            # Iterate through each result in
            if result is None:
                continue

            if 'skip_flag' in result:
                if result['skip_flag']:
                    print(f"\t skipping rank {result['rank']}" )
                    continue

            N_saved.append(result['Ns'])
            N_culled.append(result['Nc'])
            N_removed.append(result['Nr'])

    N_saved = np.array(N_saved)
    N_culled = np.array(N_culled)
    N_removed = np.array(N_removed)

    payoff = N_saved / (N_removed * N_culled)

    order = np.argsort(payoff)
    payoff = payoff[order]
    N_saved = N_saved[order]
    N_culled = N_culled[order]

    if plot:
        plot_payoff_efficiencies_1(payoff, title)

    return payoff, N_saved, N_culled, N_removed


def plot_payoff_efficiencies_1(payoff: np.ndarray, title: Optional[str] = None):
    """
    Plot payoff found from scenario test.
    """
    if title:
        plt.title(title)
    plt.plot(np.arange(len(payoff), 0, -1), payoff)
    plt.scatter(np.arange(len(payoff), 0, -1), payoff)
    plt.xlabel('rank')
    plt.ylabel('Ns/Nc')
    plt.yscale('log')
    plt.xscale('log')
    plt.show()


def plot_spatial_payoff_rank(R0_domain: np.ndarray, payoff_store: dict, rank: int,
                             title: Optional[str] = None, save: Optional[bool] = False):
    """
        For a given scenario, plot the map of the containment/

    :param R0_domain: the raw R0_values for a fitted parameter-combination
    :param payoff_store: the dictionary-struct containing information about the payoffs vs iteration
    :param rank: plot the nth-ranked scenario.
    :param title: display title on plot
    :return:
    """
    rank_epi_c = None
    rank_payoff = None
    rank_cull_line = None
    rank_cull_line_indices = None

    for epi_c, results in payoff_store.items():
        for cull_line, payoff in results.items():
            if payoff['rank'] == rank:
                rank_epi_c = epi_c
                rank_payoff = payoff
                rank_cull_line = cull_line
                rank_cull_line_indices = payoff['frag_line_indices']
                if 'skip_flag' in payoff:
                    if payoff['skip_flag']:
                        msg = 'Scenario is omitted from over-beta payoff analysis'
                        warnings.warn(msg)
                break

    if rank_cull_line is None or rank_payoff is None or rank_epi_c is None:
        msg = f'Did not find rank {rank} payoff data!'
        warnings.warn(msg)
        return

    colors = ['white', 'C0', 'C1']
    nbins = len(colors)
    cmap_name = 'my_list'

    msg = f'rank {rank}, epicenter : {rank_epi_c}, cull lines : {rank_cull_line}' \
          f' number saved : {rank_payoff["Ns"]}, ' \
          f' number removed : {rank_payoff["Nr"]}, ' \
          f' number culled : {rank_payoff["Nc"]}, '\
          f' payoff : {rank_payoff["Ns"] / rank_payoff["Nc"]}, '

    msg = msg + f" skipped/ignore : {rank_payoff['skip_flag']} " if 'skip_flag' in rank_payoff else msg

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(msg)

    R0_domain_ = np.copy(R0_domain)
    R0_domain[rank_cull_line_indices] = 0
    R0_domain, _, ids = rank_cluster_map(R0_domain)
    saved_ids = R0_domain[rank_epi_c[0], rank_epi_c[1]]

    R0_domain_[rank_cull_line_indices] = 0
    for id_ in ids:
        if id_ == saved_ids:
            continue
        R0_domain_[np.where(R0_domain == id_)] = 1

    R0_domain_[np.where(R0_domain == saved_ids)] = 2

    for culled_ind in range(len(rank_cull_line_indices[0])):
        row = rank_cull_line_indices[0][culled_ind]
        col = rank_cull_line_indices[1][culled_ind]
        plt.scatter(col, row, marker='x', color='r', s=75)

    plt.scatter(rank_epi_c[1], rank_epi_c[0], marker='x', color='black', s=100)
    cm = LinearSegmentedColormap.from_list(cmap_name, colors, N=nbins)
    im = plt.imshow(R0_domain_, cmap=cm, alpha=0.80)
    plt.colorbar(im)
    if title:
        plt.title(title)

    if save:
        plt.savefig('containment_scenario{}.pdf')

    plt.show()

def plot_cluster_size_distribution(cluster_sizes: np.array, betas: np.ndarray, save: bool = False):
    """
    For a single domain, plot the cluster-size distribution
    :param cluster_sizes:
    :return:
    """

    fig, ax = plt.subplots(figsize=(8, 6))
    assert len(betas) == len(cluster_sizes)
    for i in range(len(betas)):
        ax.plot(np.arange(1, len(cluster_sizes[i])+1), cluster_sizes[i], label=fr'$\beta$ = {round(betas[i], 6)}')
        ax.scatter(np.arange(1, len(cluster_sizes[i])+1), cluster_sizes[i])

    plt.legend()
    plt.yscale('log')
    plt.xscale('log')
    if save:
        plt.savefig('cluster_size_dist.pdf')
    plt.show()
