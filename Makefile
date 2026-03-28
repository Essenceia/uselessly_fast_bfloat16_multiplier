SIM ?= verilator

PROJET_NAME := tt_um_essen
SRC_DIR := src
BF16_SRC_DIR := $(SRC_DIR)/bf16/src
CONF := conf
WAIVER_FILE := waiver.vlt

# Lint variables.
LINT_FLAGS :=
ifeq ($(SIM),icarus)
LINT_FLAGS +=-Wall -g2012 $(if $(assert),-gassertions) -gstrict-expr-width
else
LINT_FLAGS += -Wall -Wpedantic -Wno-GENUNNAMED -Wno-LATCH -Wno-IMPLICIT
LINT_FLAGS += -Wno-DECLFILENAME
LINT_FLAGS += -Ilib
endif

.PHONY: lint

# Lint commands.
ifeq ($(SIM),icarus)
define LINT
	mkdir -p build
	iverilog $(LINT_FLAGS) -s $2 -o $(BUILD_DIR)/$2 $1
endef
else
	
define LINT
	mkdir -p build
	verilator $(CONF)/$(WAIVER_FILE) --lint-only $(LINT_FLAGS) --no-timing $1 --top $2
endef
endif

########
# Lint #
########

entry_deps := $(wildcard $(SRC_DIR)/*.v) $(wildcard $(BF16_SRC_DIR)/*.v)

lint: $(entry_deps)
	$(call LINT,$^,$(PROJET_NAME))

