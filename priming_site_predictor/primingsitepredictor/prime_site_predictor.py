"""Main module for Priming Site Predictor."""
import math
import logging
import pandas as pd  # type: ignore

LOG = logging.getLogger(__name__)


# pylint: disable=R0903
class CreatePrimer:
    """Create an instance of a primer of a desired length \
        and primer name which can be saved as a fasta file.

    By default the length is 15 and name is primer.
    """

    def __init__(self, name='primer', primerlength=15):
        """Initiate function."""
        self.name = name
        self.primer_length = primerlength
        self.primer_sequence = 'T'*self.primer_length
        self.lines = [f'<{self.name}', self.primer_sequence]

    def create_fasta(self):
        """Create primer fasta file."""
        primer = self.lines
        LOG.info("Created primer.")
        with open(f'{self.name}.fasta', 'w', encoding="utf-8") as file:
            file.write('\n'.join(self.lines))
        return primer


# pylint: disable=R0913
class PrimingSitePredictor:
    """Generate primer sites based on RIBlast results."""

    # pylint: disable=R0913
    def __init__(
            self, fasta_file, primer_sequence, energy_cutoff,
            riblast_output, output_filename
            ):
        """Initiate."""
        self.fasta_file = fasta_file
        self.primer_sequence = primer_sequence
        self.energy_cutoff = energy_cutoff
        self.riblast_output = riblast_output
        self.output_filename = output_filename

    def calculate_energy(self, value):
        """Calculate hybridization energy."""
        energy_constant = 1.380649e-23*298
        kcalmol_joul = 6.9477*10**-21
        return (math.exp(-float(value)*kcalmol_joul/energy_constant))

    def create_list_from_output(self):
        """Create list from output."""
        firstline = 3
        interaction_list = []
        with open(self.riblast_output, 'r', encoding="utf-8") as file:
            raw_interactions = file.readlines()[firstline:]
        number_entries = len(raw_interactions)

        for i in range(0, number_entries-1):
            current_interaction = raw_interactions[i].strip(
                ' \n').replace('(', '').replace(')', '').replace(
                '-', ',').replace(':', ',').split(',')
            interaction_list.append(current_interaction)

        return interaction_list

    def create_pandas_df(self):
        """Create interaction df."""
        interaction_list = self.create_list_from_output()
        interaction_df = pd.DataFrame(interaction_list)
        interaction_df['Number_of_interactions'] = int(0)
        interaction_df['Interaction_Energy'] = float(0)
        transcript = 3
        energy = 5

        for _ in interaction_df.index:
            interaction_df['Number_of_interactions'] = interaction_df[
                transcript
                ].apply(
                lambda x: interaction_df[transcript].value_counts()[x]
            )
            interaction_df['Interaction_Energy'] = interaction_df[
                energy
                ].apply(self.calculate_energy)

        LOG.info("Calculating normalised interaction energies...")
        interaction_df['Normalised_interaction_energy'] = interaction_df[
            'Interaction_Energy']/interaction_df['Number_of_interactions']

        return interaction_df

    def generate_gtf(self):
        """Generate gtf file."""
        interaction_df = self.create_pandas_df()
        result = str()

        for index in interaction_df.index:
            result += (
                str(interaction_df[3][index])
                + '\tRIBlast\tPriming_site\t'
                + str(interaction_df[13][index])
                + '\t'
                + str(interaction_df[12][index])
                + '\t.\t+\t.\t'
                + 'Interaction_Energy' + '\t'
                + str(interaction_df[
                    "Normalised_interaction_energy"
                    ][index])
                + '\n'
            )

        LOG.info("Generating output gtf file...")
        with open(self.output_filename, 'w', encoding="utf-8") as file:
            file.write(result)
            return result
