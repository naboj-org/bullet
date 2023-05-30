from competitions.branches import Branch
from countries.factories.branchcountry import BranchCountryFactory


def create_branch_countries(branch: Branch):
    BranchCountryFactory.create_batch(120, branch=branch)
