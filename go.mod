module github.com/artur-rios/heimdall-docs

go 1.26.7

// Pinned: v0.16.0 moved Docsy's layouts/assets into a submodule the Hugo
// Module zip omits, so it resolves but builds no output.
require github.com/google/docsy v0.15.0 // indirect
