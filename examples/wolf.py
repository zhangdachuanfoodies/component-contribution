import sys, logging, os

REACTION_FNAME = 'examples/wolf_reactions.txt'
PYTHON_BIN = 'python'
PYTHON_SCRIPT_FNAME = 'python/component_contribution.py'

def python_main():
    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)
    from python.component_contribution import ComponentContribution
    from python.kegg_model import KeggModel

    cc = ComponentContribution.init()
    reaction_strings = open(REACTION_FNAME, 'r').readlines()
    model = KeggModel.from_formulas(reaction_strings)

    model.add_thermo(cc)
    dG0_prime, dG0_std = model.get_transformed_dG0(7.0, 0.2, 298.15)
    for i, r in enumerate(reaction_strings):
        print '-'*50
        print r.strip()
        print "dG0 = %8.1f +- %5.1f" % (dG0_prime[i, 0], dG0_std[i, i] * 1.96)

if __name__ == '__main__':
    pwd = os.path.realpath(os.path.curdir)
    _, directory = os.path.split(pwd)
    if directory == 'examples':
        sys.path.append(os.path.abspath('..'))
        os.chdir('..')
        
    python_main()
