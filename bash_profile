export PATH=/Users/huanle/homebrew/bin:/Users/huanle/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Users/huanle/Library/Python/3.8/bin
SSH_ENV="${HOME}/.ssh/agent-environment"
mkdir -p ${HOME}/.ssh

function start_agent {
	echo "Initialising new SSH agent..."
	/usr/bin/ssh-agent | sed 's/^echo/#echo/' > "${SSH_ENV}"
	chmod 600 "${SSH_ENV}"
	. "${SSH_ENV}" > /dev/null
	/usr/bin/ssh-add > /dev/null
	/usr/bin/ssh-add -l
}

# Source SSH settings, if applicable
if [ -f "${SSH_ENV}" ]; then
	. "${SSH_ENV}" > /dev/null
	ps -ef | grep ${SSH_AGENT_PID} | grep ssh-agent$ > /dev/null || start_agent
else
	start_agent
fi
