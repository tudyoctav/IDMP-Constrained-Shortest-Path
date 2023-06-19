SYSTEM     = x86-64_linux
LIBFORMAT  = static_pic
BUILD_DIR = build/

#------------------------------------------------------------
#
# Change these values to point to the directory CPLEx and Concert respectively
#
#------------------------------------------------------------

CPLEXDIR      = /mnt/Windows/temp/cplex
CONCERTDIR    = /mnt/Windows/temp/concert

# ---------------------------------------------------------------------
# Compiler selection 
# ---------------------------------------------------------------------

CCC = g++

# ---------------------------------------------------------------------
# Compiler options 
# ---------------------------------------------------------------------

CCOPT = -m64 -fPIC -fno-strict-aliasing -fexceptions -DNDEBUG

# ---------------------------------------------------------------------
# Link options and libraries
# ---------------------------------------------------------------------

CPLEXBINDIR   = $(CPLEXDIR)/bin/$(BINDIST)
CPLEXLIBDIR   = $(CPLEXDIR)/lib/$(SYSTEM)/$(LIBFORMAT)
CONCERTLIBDIR = $(CONCERTDIR)/lib/$(SYSTEM)/$(LIBFORMAT)

# For dynamic linking
CPLEXBINDIR   = $(CPLEXDIR)/bin/$(SYSTEM)
CPLEXLIB      = cplex$(dynamic:yes=2211)

CCLNDIRS  = -L$(CPLEXLIBDIR) -L$(CONCERTLIBDIR) $(dynamic:yes=-L$(CPLEXBINDIR))
CLNDIRS   = -L$(CPLEXLIBDIR) $(dynamic:yes=-L$(CPLEXBINDIR))
CCLNFLAGS = -lconcert -lilocplex -l$(CPLEXLIB) -lm -lpthread -ldl
CLNFLAGS  = -l$(CPLEXLIB) -lm -lpthread -ldl


all:
	make RCSP-MIP

CONCERTINCDIR = $(CONCERTDIR)/include
CPLEXINCDIR   = $(CPLEXDIR)/include


CCFLAGS = $(CCOPT) -I$(CPLEXINCDIR) -I$(CONCERTINCDIR) 



# test:
#     $(foreach var,$(.VARIABLES),$(info $(var) = $($(var))))

# ------------------------------------------------------------

.PHONY: clean
clean :
	rm -r $(BUILD_DIR)
	/bin/rm -rf *.o *~ *.class
	/bin/rm -rf $(C_EX) $(CX_EX) $(CPP_EX)
	/bin/rm -rf *.mps *.ord *.sos *.lp *.sav *.net *.msg *.log *.clp

# ------------------------------------------------------------
#
# The examples
#

CC_FILES = $(wildcard *.cpp) $(wildcard **/*.cpp) 
O_FILES = $(addprefix $(BUILD_DIR),$(subst .cpp,.o,$(CC_FILES)))
program = $(BUILD_DIR)RCSP-MIP

.PHONY: test
test:
	# $(O_FILES)


.PHONY: compile
compile: $(program)

$(program): $(O_FILES)
	$(CCC) $(CCFLAGS) $(CCLNDIRS) -o $(program) ${O_FILES} $(CCLNFLAGS)
$(O_FILES): ${CC_FILES}
	@mkdir -p $(@D)
	$(CCC) -c $(CCFLAGS) $(subst $(BUILD_DIR),,$(subst .o,.cpp,$@)) $(CCFLAGS) $(CCLNDIRS) -o $@

$(BUILD_DIR) $(BUILD_DIR)lib:
	mkdir --parents $(BUILD_DIR)lib

# Local Variables:
# mode: makefile
# End:
