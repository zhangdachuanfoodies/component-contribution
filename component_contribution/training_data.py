# -*- encoding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2013 The Weizmann Institute of Science.
# Copyright (c) 2018 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import

import logging
from gzip import GzipFile

import numpy as np
import pandas as pd
from importlib_resources import open_binary, open_text

import component_contribution.data as data
from component_contribution.thermodynamic_constants import R


LOGGER = logging.getLogger(__name__)


def read_tecrdb():
    """
    Load a data frame with information from the TECRdb (NIST).

    The component-contribution package distributes data tables with
    information on the 'thermodynamics of enzyme-catalyzed reactions'[1, 2]_
    that are used as training data.

    Returns
    -------
    pandas.DataFrame

    References
    ----------
    .. [1] Goldberg, Robert N., Yadu B. Tewari, and Talapady N. Bhat.
           “Thermodynamics of Enzyme-Catalyzed Reactions—a Database for
           Quantitative Biochemistry.” Bioinformatics 20, no. 16 (November 1,
           2004): 2874–77. https://doi.org/10.1093/bioinformatics/bth314.
    .. [2] http://xpdb.nist.gov/enzyme_thermodynamics/

    """
    columns = [
        "url",
        "reference",
        "method",
        "eval",
        "ec_number",
        "name",
        "definition_kegg",
        "description",
        "standard_equilibrium_constant",
        "equilibrium_constant",
        "temperature",
        "isoelectric_point",
        "ph_value",
        "log_magnesium_concentration"
    ]
    with open_binary(data, "TECRDB.tsv.gz") as archive:
        with GzipFile(fileobj=archive) as file_handle:
            table = pd.read_table(file_handle, sep="\t", header=None,
                                  index_col=False, names=columns)
    LOGGER.debug("Read %d rows.", len(table))
    table["gibbs_energy_prime"] = \
        -R * table["temperature"] * np.log(table["equilibrium_constant"])
    return table
    # [[
    #     "reaction",
    #     "delta_gibbs_zero",
    #     "temperature",
    #     "isoelectric_point",
    #     "ph_value",
    #     "log_magnesium_concentration"
    #     "weight",
    #     "is_balanced",
    #     "reference",
    #     "description"
    # ]]


def read_formations():
    columns = [
        "kegg_id",
        "name",
        "gibbs_energy_prime",
        "ph_value",
        "isoelectric_point",
        "log_magnesium_concentration",
        "temperature",
        "decompose",
        "reference",
        "remark"
    ]
    # Replace the header by skipping the first row.
    with open_text(data, "formation_energies_transformed.tsv") as file_handle:
        table = pd.read_table(file_handle, sep="\t", header=None,
                              skiprows=1, index_col=False, names=columns)
    LOGGER.debug("Read %d rows.", len(table))
    table["decompose"] = (table["decompose"] == 1)
    return table


def read_redox():
    columns = [
        "name",
        "kegg_id_oxidized",
        "number_protons_oxidized",
        "charge_oxidized",
        "kegg_id_reduced",
        "number_protons_reduced",
        "charge_reduced",
        "nernst_potential_prime",
        "ph_value",
        "isoelectric_point",
        "log_magnesium_concentration",
        "temperature",
        "reference"
    ]
    with open_text(data, "redox.tsv") as file_handle:
        table = pd.read_table(file_handle, sep="\t", header=None,
                              skiprows=1, index_col=False, names=columns)
    LOGGER.debug("Read %d rows.", len(table))
    return table


# TODO: Refactor training data. Do **not** remove commented code.

# class TrainingData(object):

    # # a dictionary of the filenames of the training data and the relative
    # # weight of each one
    # FNAME_DICT = {'TECRDB' : ('../data/TECRDB.tsv', 1.0),
    #               'FORMATION' : ('../data/formation_energies_transformed.tsv', 1.0),
    #               'REDOX' : ('../data/redox.tsv', 1.0)}

    # def __del__(self):
    #     self.ccache.dump()

    # def __init__(self):
    #     self.ccache = CompoundCache()

        # thermo_params, self.cids_that_dont_decompose = TrainingData.get_all_thermo_params()

        # cids = set()
        # for d in thermo_params:
        #     cids = cids.union(d['reaction'].keys())
        # cids = sorted(cids)

        # # convert the list of reactions in sparse notation into a full
        # # stoichiometric matrix, where the rows (compounds) are according to the
        # # CID list 'cids'.
        # self.S = np.zeros((len(cids), len(thermo_params)))
        # for k, d in enumerate(thermo_params):
        #     for cid, coeff in d['reaction'].items():
        #         self.S[cids.index(cid), k] = coeff

        # self.cids = cids

        # self.dG0_prime = np.array([d['dG\'0'] for d in thermo_params])
        # self.T = np.array([d['T'] for d in thermo_params])
        # self.I = np.array([d['I'] for d in thermo_params])
        # self.pH = np.array([d['pH'] for d in thermo_params])
        # self.pMg = np.array([d['pMg'] for d in thermo_params])
        # self.weight = np.array([d['weight'] for d in thermo_params])
        # self.reference = [d['reference'] for d in thermo_params]
        # self.description = [d['description'] for d in thermo_params]
        # rxn_inds_to_balance = [i for i in range(len(thermo_params))
        #                        if thermo_params[i]['balance']]

        # self.balance_reactions(rxn_inds_to_balance)

        # self.reverse_transform()

    # def savemat(self, file_name):
    #     """
    #         Write all training data to a Matlab file.

        #     Arguments:
        #         file_name - str or file-like object to which data will be written
        # """
        # d = {'dG0_prime': self.dG0_prime,
        #      'dG0': self.dG0,
        #      'T': self.T,
        #      'I': self.I,
        #      'pH': self.pH,
        #      'pMg': self.pMg,
        #      'weight': self.weight,
        #      'cids': self.cids,
        #      'S': self.S}
        # savemat(file_name, d, oned_as='row')

    # def savecsv(self, fname):
    #     csv_output = csv.writer(open(fname, 'w'))
    #     csv_output.writerow(['reaction', 'T', 'I', 'pH', 'reference', 'dG0', 'dG0_prime'])
    #     for j in range(self.S.shape[1]):
    #         sparse = {self.cids[i]: self.S[i, j] for i in range(self.S.shape[0])}
    #         r_string = KeggReaction(sparse).write_formula()
    #         csv_output.writerow([r_string, self.T[j], self.I[j], self.pH[j],
    #                              self.reference[j], self.dG0[j], self.dG0_prime[j]])

    # @staticmethod
    # def str2double(s):
    #     """
    #         casts a string to float, but if the string is empty return NaN
    #     """
    #     if s == '':
    #         return np.nan
    #     else:
    #         return float(s)

    # @staticmethod
    # def read_tecrdb(fname, weight):
    #     """Read the raw data of TECRDB (NIST)"""
    #     thermo_params = [] # columns are: reaction, dG'0, T, I, pH, pMg, weight, balance?

        # headers = ["URL", "REF_ID", "METHOD", "EVAL", "EC", "ENZYME NAME",
        #            "REACTION IN KEGG IDS", "REACTION IN COMPOUND NAMES",
        #            "K", "K'", "T", "I", "pH", "pMg"]

        # for row_list in csv.reader(open(fname, 'r'), delimiter='\t'):
        #     if row_list == []:
        #         continue
        #     row = dict(zip(headers, row_list))
        #     if (row['K\''] == '') or (row['T'] == '') or (row['pH'] == ''):
        #         continue

            # # parse the reaction
            # reaction = KeggReaction.parse_formula(row['REACTION IN KEGG IDS'], arrow='=')

            # # calculate dG'0
            # dG0_prime = -R * TrainingData.str2double(row['T']) * \
            #                  np.log(TrainingData.str2double(row['K\'']))
            # try:
            #     thermo_params.append({'reaction': reaction,
            #                           'dG\'0' : dG0_prime,
            #                           'T': TrainingData.str2double(row['T']),
            #                           'I': TrainingData.str2double(row['I']),
            #                           'pH': TrainingData.str2double(row['pH']),
            #                           'pMg': TrainingData.str2double(row['pMg']),
            #                           'weight': weight,
            #                           'balance': True,
            #                           'reference': row['REF_ID'],
            #                           'description': row['REACTION IN COMPOUND NAMES']})
            # except ValueError:
            #     raise Exception('Cannot parse row: ' + str(row))

        # logging.debug('Successfully added %d reactions from TECRDB' % len(thermo_params))
        # return thermo_params

    # @staticmethod
    # def read_formations(fname, weight):
    #     """Read the Formation Energy data"""

        # # columns are: reaction, dG'0, T, I, pH, pMg, weight, balance?
        # thermo_params = []
        # cids_that_dont_decompose = set()

        # # fields are: cid, name, dG'0, pH, I, pMg, T, decompose?,
        # #             compound_ref, remark
        # for row in csv.DictReader(open(fname, 'r'), delimiter='\t'):
        #     if int(row['decompose']) == 0:
        #         cids_that_dont_decompose.add(row['cid'])
        #     if row['dG\'0'] != '':
        #         rxn = KeggReaction({row['cid'] : 1})
        #         thermo_params.append({'reaction': rxn,
        #                               'dG\'0' : TrainingData.str2double(row['dG\'0']),
        #                               'T': TrainingData.str2double(row['T']),
        #                               'I': TrainingData.str2double(row['I']),
        #                               'pH': TrainingData.str2double(row['pH']),
        #                               'pMg': TrainingData.str2double(row['pMg']),
        #                               'weight': weight,
        #                               'balance': False,
        #                               'reference': row['compound_ref'],
        #                               'description': row['name'] + ' formation'})

        # logging.debug('Successfully added %d formation energies' % len(thermo_params))
        # return thermo_params, cids_that_dont_decompose

    # @staticmethod
    # def read_redox(fname, weight):
    #     """Read the Reduction potential data"""
    #     # columns are: reaction, dG'0, T, I, pH, pMg, weight, balance?
    #     thermo_params = []

        # # fields are: name, CID_ox, nH_ox, charge_ox, CID_red,
        # #             nH_red, charge_red, E'0, pH, I, pMg, T, ref
        # for row in csv.DictReader(open(fname, 'r'), delimiter='\t'):
        #     delta_nH = TrainingData.str2double(row['nH_red']) - \
        #                TrainingData.str2double(row['nH_ox'])
        #     delta_charge = TrainingData.str2double(row['charge_red']) - \
        #                    TrainingData.str2double(row['charge_ox'])
        #     delta_e = delta_nH - delta_charge
        #     dG0_prime = -F * TrainingData.str2double(row['E\'0']) * delta_e
        #     rxn = KeggReaction({row['CID_ox'] : -1, row['CID_red'] : 1})
        #     thermo_params.append({'reaction': rxn,
        #                           'dG\'0' : dG0_prime,
        #                           'T': TrainingData.str2double(row['T']),
        #                           'I': TrainingData.str2double(row['I']),
        #                           'pH': TrainingData.str2double(row['pH']),
        #                           'pMg': TrainingData.str2double(row['pMg']),
        #                           'weight': weight,
        #                           'balance': False,
        #                           'reference': row['ref'],
        #                           'description': row['name'] + ' redox'})

        # logging.debug('Successfully added %d redox potentials' % len(thermo_params))
        # return thermo_params

    # @staticmethod
    # def get_all_thermo_params():
    #     base_path = os.path.split(os.path.realpath(__file__))[0]

        # fname, weight = TrainingData.FNAME_DICT['TECRDB']
        # fname = os.path.join(base_path, fname)
        # tecrdb_params = TrainingData.read_tecrdb(fname, weight)

        # fname, weight = TrainingData.FNAME_DICT['FORMATION']
        # fname = os.path.join(base_path, fname)
        # formation_params, cids_that_dont_decompose = TrainingData.read_formations(fname, weight)

        # fname, weight = TrainingData.FNAME_DICT['REDOX']
        # fname = os.path.join(base_path, fname)
        # redox_params = TrainingData.read_redox(fname, weight)

        # thermo_params = tecrdb_params + formation_params + redox_params
        # return thermo_params, cids_that_dont_decompose

    # def balance_reactions(self, rxn_inds_to_balance):
    #     """
    #         use the chemical formulas from the InChIs to verify that each and every
    #         reaction is balanced
    #     """
    #     elements, Ematrix = self.ccache.get_element_matrix(self.cids)
    #     cpd_inds_without_formula = list(np.nonzero(np.any(np.isnan(Ematrix), 1))[0].flat)
    #     Ematrix[np.isnan(Ematrix)] = 0

        # S_without_formula = self.S[cpd_inds_without_formula, :]
        # rxn_inds_without_formula = np.nonzero(np.any(S_without_formula != 0, 0))[0]
        # rxn_inds_to_balance = set(rxn_inds_to_balance).difference(rxn_inds_without_formula)

        # # need to check that all elements are balanced (except H, but including e-)
        # # if only O is not balanced, add water molecules
        # if 'O' in elements:
        #     i_H2O = self.cids.index('C00001')
        #     j_O = elements.index('O')
        #     conserved = np.dot(Ematrix.T, self.S)
        #     for k in rxn_inds_to_balance:
        #         self.S[i_H2O, k] = self.S[i_H2O, k] - conserved[j_O, k]

        # # recalculate conservation matrix
        # conserved = Ematrix.T * self.S

        # rxn_inds_to_remove = [k for k in rxn_inds_to_balance
        #                       if np.any(conserved[:, k] != 0, 0)]

        # for k in rxn_inds_to_remove:
        #     sprs = {}
        #     for i in np.nonzero(self.S[:, k])[0]:
        #         sprs[self.cids[i]] = self.S[i, k]
        #     reaction = KeggReaction(sprs)
        #     logging.debug('unbalanced reaction #%d: %s' %
        #                   (k, reaction.write_formula()))
        #     for j in np.where(conserved[:, k])[0].flat:
        #         logging.debug('there are %d more %s atoms on the right-hand side' %
        #                       (conserved[j, k], elements[j]))

        # rxn_inds_to_keep = \
        #     set(range(self.S.shape[1])).difference(rxn_inds_to_remove)

        # rxn_inds_to_keep = sorted(rxn_inds_to_keep)

        # self.S = self.S[:, rxn_inds_to_keep]
        # self.dG0_prime = self.dG0_prime[rxn_inds_to_keep]
        # self.T = self.T[rxn_inds_to_keep]
        # self.I = self.I[rxn_inds_to_keep]
        # self.pH = self.pH[rxn_inds_to_keep]
        # self.pMg = self.pMg[rxn_inds_to_keep]
        # self.weight = self.weight[rxn_inds_to_keep]
        # self.reference = [self.reference[i] for i in rxn_inds_to_keep]
        # self.description = [self.description[i] for i in rxn_inds_to_keep]

        # logging.debug('After removing %d unbalanced reactions, the stoichiometric '
        #               'matrix contains: '
        #               '%d compounds and %d reactions' %
        #               (len(rxn_inds_to_remove), self.S.shape[0], self.S.shape[1]))

    # def reverse_transform(self):
    #     """
    #         Calculate the reverse transform for all reactions in training_data.
    #     """
    #     n_rxns = self.S.shape[1]
    #     reverse_ddG0 = np.zeros(n_rxns)
    #     self.I[np.isnan(self.I)] = 0.25 # default ionic strength is 0.25M
    #     self.pMg[np.isnan(self.pMg)] = 14 # default pMg is 14
    #     for i in range(n_rxns):
    #         for j in np.nonzero(self.S[:, i])[0]:
    #             cid = self.cids[j]
    #             if cid == 'C00080': # H+ should be ignored in the Legendre transform
    #                 continue
    #             comp = self.ccache.get_compound(cid)
    #             ddG0 = comp.transform_p_h_7(self.pH[i], self.I[i], self.T[i])
    #             reverse_ddG0[i] = reverse_ddG0[i] + ddG0 * self.S[j, i]

        # self.dG0 = self.dG0_prime - reverse_ddG0

# if __name__ == '__main__':
#     import argparse
#     parser = argparse.ArgumentParser(description=
#         'Prepare all thermodynamic training data in a .mat file for running '
#         'component contribution.')
#     parser.add_argument('outfile', type=argparse.FileType('w'),
#                        help='the path to the .mat file that should be written '
#                        'containing the training data')

    # args = parser.parse_args()
    # td = TrainingData()
    # td.savemat(args.outfile)
