;; Disable lock-files; there is a bug somewhere in create-react-app that chokes
;; on emacs lock files
;; Also make sure to use spaces as indentation
((nil . ((create-lockfiles . nil)
	 (indent-tabs-mode . nil)
	 )))
