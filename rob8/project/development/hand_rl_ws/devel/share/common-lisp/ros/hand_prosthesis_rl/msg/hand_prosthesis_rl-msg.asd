
(cl:in-package :asdf)

(defsystem "hand_prosthesis_rl-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "RLExperimentInfo" :depends-on ("_package_RLExperimentInfo"))
    (:file "_package_RLExperimentInfo" :depends-on ("_package"))
  ))