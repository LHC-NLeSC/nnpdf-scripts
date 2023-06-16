# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# User specific environment
if ! [[ "$PATH" =~ "$HOME/.local/bin:$HOME/bin:" ]]
then
    PATH="$HOME/.local/bin:$HOME/bin:$PATH"
fi
export PATH

function anaconda {
    # Load modules
    module load 2022
    module load Anaconda3/2022.05

    # Define common directory path
    local mamba_path="/gpfs/admin/_hpc/sw/arch/AMD-ZEN2/RHEL8/EB_production/2022/software/Mamba/4.14.0-0"

    # Begin conda initialization
    local conda_bin="$mamba_path/bin/conda"
    local conda_setup="$("$conda_bin" 'shell.bash' 'hook' 2> /dev/null)"
    
    # If conda initialization is successful, execute the setup
    if [ $? -eq 0 ]; then 
        eval "$conda_setup"
    else
        # Try to source conda.sh if it exists. If it doesn't, add Mamba's bin to PATH
        local conda_sh="$mamba_path/etc/profile.d/conda.sh"
        if [ -f "$conda_sh" ]; then
            source "$conda_sh"
        else
            export PATH="$mamba_path/bin:$PATH"
        fi
    fi
    
    unset conda_setup  # Clean up setup variable

    # Source mamba.sh if it exists for Mamba specific settings
    local mamba_sh_path="$mamba_path/etc/profile.d/mamba.sh"
    if [ -f "$mamba_sh_path" ]; then
        source "$mamba_sh_path"
    fi
}
 
