$env:ANTHROPIC_BASE_URL="http://localhost:20128"
$env:ANTHROPIC_AUTH_TOKEN="sk-c4c45dda1c81700d-936fa1-f9e7eb38"
$env:ANTHROPIC_MODEL="aiwithshivank"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL="aiwithshivank"
$env:ANTHROPIC_DEFAULT_SONNET_MODEL="aiwithshivank"
$env:ANTHROPIC_DEFAULT_FABLE_MODEL="aiwithshivank"
remove-item env:ANTHROPIC_API_KEY -ErrorAction SilentlyContinue
