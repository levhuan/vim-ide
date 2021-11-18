#!//usr/bin/env python3

import argparse
import os
import json

DOTVIMRC_BEGIN = '''
set nocompatible
filetype on
filetype plugin on
filetype indent on
syntax on
set ruler
set hlsearch
set incsearch
set showcmd

call plug#begin('{vp_plugin_path}')
'''

DOTVIMRC_END = '''
call plug#end()

" Add git branch to the status line
function! GitBranch()
  return system("git rev-parse --abbrev-ref HEAD 2>/dev/null | tr -d \'\\n\'")
  endfunction

function! StatuslineGit()
  let l:branchname = GitBranch()
   return strlen(l:branchname) > 0?'  '.l:branchname.' ':''
endfunction

set statusline=
set statusline+=%#PmenuSel#
set statusline+=%{StatuslineGit()}
set statusline+=%#LineNr#
set statusline+=\ %f
set statusline+=%m
set statusline+=%=
set statusline+=%#CursorColumn#
set statusline+=\ %y
set statusline+=\ %{&fileencoding?&fileencoding:&encoding}
set statusline+=\[%{&fileformat}\]
set statusline+=\ %p%%
set statusline+=\ %l:%c
set statusline+=\ 
'''

#
# vim-plug hotkeys. Should have added a global list of hotkeys
#
PLUG_HOTKEYS = '''
nmap <C-p>i :PlugInstall<CR>
nmap <C-p>u :PlugUpdate<CR>
nmap <C-p>s :PlugStatus<CR>
nmap <C-p>d :PlugDiff<CR>
nmap <C-p><C-u> :PlugUpgrade<CR>
'''

MY_DOTVIMRC = os.path.expanduser('~/.vimrc')
MY_DOTVIM = os.path.expanduser('~/.vim')

class VimPlug(object):
    def __init__(self, output):
        self._output_dir = output
        self._dotvim_dir = output + "/dotvim"
        self._plugin_dir = output + "/vp-plugins"
        self._plugins = dict()
        CURL = "curl -fLo {output}/dotvim/autoload/plug.vim --create-dirs ".format(output= output)
        VIM_PLUG_URI = "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim"
        os.system(CURL +  VIM_PLUG_URI)


    def add_vp_plugins(self, plugins):
        """ Create dir to install vim-plug plugins """
        self._plugins = plugins
        os.makedirs(self._plugin_dir, exist_ok=True)

    def _setup_vp_plugins_hotkeys(self):
        hk_file = open(self._plugin_dir + '/hotkeys.vim', 'w+')
        hk_file.write('" key map for vim-plug command')
        hk_file.write(PLUG_HOTKEYS)
        for p in self._plugins:
            try:
                hotkeys = self._plugins[p]['hotkeys']
                hk_file.write('" key map for plugin {p}\n'.format(p=p))
                for k in hotkeys:
                    hk_file.write(k + ' ' +  hotkeys[k] + '\n')
            except KeyError:
                print('No hotkeys for {p}'.format(p=p))
            else:
                print('finished processing {p}'.format(p=p))
            finally:
                pass
        hk_file.close()

    def _generate_vimrc(self):
        """ generate vimrc file in <path> """
        os.makedirs(self._dotvim_dir, exist_ok=True)
        vimrc_file = open(self._dotvim_dir + "/vimrc", "w+")
        vimrc_file.write(DOTVIMRC_BEGIN.format(vp_plugin_path=self._plugin_dir))
        for p in self._plugins:
            plugin_cmd = str()
            try:
                plugin_cmd = "Plug '{p}', {config}\n".format(p=p, config=self._plugins[p]['config'])
            except KeyError:
                plugin_cmd = "Plug '{p}'\n".format(p=p)
            finally:
                vimrc_file.write(plugin_cmd)

        vimrc_file.write(DOTVIMRC_END)
        vimrc_file.write("source {vp_path}/hotkeys.vim\n".format(vp_path=self._plugin_dir))
        vimrc_file.close()
        

    def generate_vimfiles(self):
        self._generate_vimrc()
        self._setup_vp_plugins_hotkeys()

    def update_user_setting(self):
        """ set up symlink to the new .vim and .vimrc """
        try:
            os.rename(MY_DOTVIMRC, MY_DOTVIMRC + '.orig')
        except FileNotFoundError:
            print('{p} not found'.format(p=MY_DOTVIMRC))
        finally:
            os.symlink(self._dotvim_dir + "/vimrc", MY_DOTVIMRC)
   
        try:
            os.rename(MY_DOTVIM, MY_DOTVIM + ".orig")
        except FileNotFoundError:
            pass
        finally:
            os.symlink(self._dotvim_dir, MY_DOTVIM)
   

parser = argparse.ArgumentParser(description ='Vim Setup Options')
parser.add_argument('--output', '-d', type=str, help='dotvim directory')
parser.add_argument('plugins', nargs='?', type=str, help='json plugin info')

OUTPUT_DIR_LAYOUT = '''
  {output}
  {output}/dotvim
  {output}/dotvim/autoload
  {output}/vp-plugins
  {output}/vimrc
'''

def main():
    args = parser.parse_args()
    if args.output is None:
        print('Specify output directory where vim scripts will be generated!')
        return

    with open(args.plugins, "+r") as ifile:
        plugins = json.load(ifile)
        v = VimPlug(args.output)
        v.add_vp_plugins(plugins)
        v.generate_vimfiles()
        v.update_user_setting()

main()
