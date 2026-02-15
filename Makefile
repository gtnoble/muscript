# Makefile for building Muslang examples

# Python interpreter (use the virtual environment if available)
VENV_PYTHON := .venv/bin/python
PYTHON := $(shell [ -f $(VENV_PYTHON) ] && echo $(VENV_PYTHON) || echo python3)
MUSLANG := $(PYTHON) -m muslang.cli

# Directories
EXAMPLES_DIR := examples

# Source files
SOURCES := $(wildcard $(EXAMPLES_DIR)/*.mus)

# Target MIDI files
MIDIS := $(SOURCES:.mus=.mid)

# Default target: build all examples
.PHONY: all
all: $(MIDIS)

# Rule to build a MIDI file from a .mus source file
$(EXAMPLES_DIR)/%.mid: $(EXAMPLES_DIR)/%.mus
	@echo "Building $@..."
	$(MUSLANG) compile $< -o $@

# Check all examples for syntax/semantic errors
.PHONY: check
check:
	@echo "Checking all examples..."
	@for file in $(SOURCES); do \
		echo "Checking $$file..."; \
		$(MUSLANG) check $$file || exit 1; \
	done
	@echo "✅ All examples are valid"

# Clean generated MIDI files
.PHONY: clean
clean:
	@echo "Cleaning generated MIDI files..."
	@rm -f $(MIDIS)
	@echo "✅ Clean complete"

# Show list of targets
.PHONY: list
list:
	@echo "Available examples:"
	@for file in $(SOURCES); do \
		echo "  - $$(basename $$file .mus)"; \
	done

# Build a specific example
.PHONY: basic_melody articulation_showcase drum_beat dynamics_demo orchestral ornaments_demo piano_voices repeat_demo rhythm_complex
basic_melody: $(EXAMPLES_DIR)/basic_melody.mid
articulation_showcase: $(EXAMPLES_DIR)/articulation_showcase.mid
drum_beat: $(EXAMPLES_DIR)/drum_beat.mid
dynamics_demo: $(EXAMPLES_DIR)/dynamics_demo.mid
orchestral: $(EXAMPLES_DIR)/orchestral.mid
ornaments_demo: $(EXAMPLES_DIR)/ornaments_demo.mid
piano_voices: $(EXAMPLES_DIR)/piano_voices.mid
repeat_demo: $(EXAMPLES_DIR)/repeat_demo.mid
rhythm_complex: $(EXAMPLES_DIR)/rhythm_complex.mid

# Help target
.PHONY: help
help:
	@echo "Muslang Examples Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make              Build all examples"
	@echo "  make all          Build all examples"
	@echo "  make check        Check all examples for errors"
	@echo "  make clean        Remove generated MIDI files"
	@echo "  make list         List all available examples"
	@echo "  make <example>    Build a specific example (e.g., make basic_melody)"
	@echo ""
	@echo "Available examples:"
	@for file in $(SOURCES); do \
		echo "  - $$(basename $$file .mus)"; \
	done
