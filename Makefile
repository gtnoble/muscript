# Makefile for building Muslang examples

# Python interpreter (use the virtual environment if available)
VENV_PYTHON := .venv/bin/python
PYTHON := $(shell [ -f $(VENV_PYTHON) ] && echo $(VENV_PYTHON) || echo python3)
MUSLANG := $(PYTHON) -m muslang.cli

# Directories
EXAMPLES_DIR := examples

# Source files
M4_SOURCES := $(wildcard $(EXAMPLES_DIR)/*.mus.m4)
GENERATED_MUS := $(M4_SOURCES:.mus.m4=.mus)
STATIC_SOURCES := $(filter-out $(GENERATED_MUS),$(wildcard $(EXAMPLES_DIR)/*.mus))
SOURCES := $(sort $(STATIC_SOURCES) $(GENERATED_MUS))

# Target MIDI files
MIDIS := $(SOURCES:.mus=.mid)

# Ensure m4 is available when preprocessing macro sources
M4 := $(shell command -v m4 2>/dev/null)

# Default target: build all examples
.PHONY: all
all: $(MIDIS)

# Rule to build a MIDI file from a .mus source file
$(EXAMPLES_DIR)/%.mid: $(EXAMPLES_DIR)/%.mus
	@echo "Building $@..."
	$(MUSLANG) compile $< -o $@

# Rule to generate a .mus file from a .mus.m4 source file
$(EXAMPLES_DIR)/%.mus: $(EXAMPLES_DIR)/%.mus.m4
	@if [ -z "$(M4)" ]; then \
		echo "❌ m4 is required but not found in PATH"; \
		exit 1; \
	fi
	@echo "Preprocessing $< -> $@..."
	m4 $< > $@

# Check all examples for syntax/semantic errors
.PHONY: check
check: $(GENERATED_MUS)
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
	@rm -f $(GENERATED_MUS)
	@echo "✅ Clean complete"

# Show list of targets
.PHONY: list
list: $(GENERATED_MUS)
	@echo "Available examples:"
	@for file in $(SOURCES); do \
		echo "  - $$(basename $$file .mus)"; \
	done

# Build a specific example
.PHONY: basic_melody articulation_showcase drum_beat dynamics_demo lofi_beat orchestral ornaments_demo piano_voices repeat_demo rhythm_complex smooth_jazz
basic_melody: $(EXAMPLES_DIR)/basic_melody.mid
articulation_showcase: $(EXAMPLES_DIR)/articulation_showcase.mid
drum_beat: $(EXAMPLES_DIR)/drum_beat.mid
dynamics_demo: $(EXAMPLES_DIR)/dynamics_demo.mid
lofi_beat: $(EXAMPLES_DIR)/lofi_beat.mid
orchestral: $(EXAMPLES_DIR)/orchestral.mid
ornaments_demo: $(EXAMPLES_DIR)/ornaments_demo.mid
piano_voices: $(EXAMPLES_DIR)/piano_voices.mid
repeat_demo: $(EXAMPLES_DIR)/repeat_demo.mid
rhythm_complex: $(EXAMPLES_DIR)/rhythm_complex.mid
smooth_jazz: $(EXAMPLES_DIR)/smooth_jazz.mid

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
