# Toolbox helpers. Skill distribution is owned by the devdocker/dotfiles chezmoi
# wiring. These commands only refresh external snapshots in the canonical tree.

skills-list:
  @bin/skillctl list

skills-check:
  @bin/skillctl check

skills-test:
  python -B -m unittest discover -s tests -v

web-clip-test:
  python -B -m unittest discover -s tests -p 'test_web_clip.py' -v

web-clip-browser-test:
  WEB_CLIP_BROWSER_TEST=1 python -B -m unittest discover -s tests -p 'test_web_clip.py' -v

skills-sync *names:
  @bin/skillctl sync {{names}}

skills-add source *args:
  @bin/skillctl add {{source}} {{args}}

web-clip url output="clips":
  @bin/web-clip {{url}} -o {{output}}

# Kept as a short alias for interactive use.
list: skills-list

# Run the focused regression test for the scheduled WezTerm sender.
test-resume-session:
  python -B -m unittest discover -s bin/tests -v
