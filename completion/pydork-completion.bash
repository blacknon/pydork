#!bash
# =======================================================

_pydork() {
  local cur
  local cmd

  cur=${COMP_WORDS[$COMP_CWORD]}
  cmd=(${COMP_WORDS[@]})

  if [[ "$cur" == -* ]]; then
    COMPREPLY=($(compgen -W "-h --help" -- $cur))
    return 0
  fi
}

complete -F _pydork -o default pydork
