# Load modules
module load 2022 TensorFlow/2.11.0-foss-2022a-CUDA-11.7.0 

# Create virtual env
python -m venv ~/nnpdf-env

# activate it
source ~/nnpdf-env/bin/activate

# install nnpdf
pip install -e .[nolha]

# this is missing somehow
pip install typing_extensions

lhapdf-management update --init
