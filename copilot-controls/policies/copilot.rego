package copilot.policy

import rego.v1

# Block suggestions that include secrets or classified patterns
deny[msg] {
  suggestion := input.suggestion
  pattern := input.blocklist[_]
  lower(suggestion) contains lower(pattern)
  msg := {"reason": "Blocked sensitive pattern", "pattern": pattern}
}

# Require issue reference format in pull requests when Copilot suggestions exceed threshold
require_issue_reference[msg] {
  input.context.pull_request
  input.statistics.copilot_accept_rate > 0.3
  not regex.match("#[0-9]+", input.context.pull_request.title)
  msg := {"reason": "Missing issue reference", "control": "CTRL-PR-01"}
}
