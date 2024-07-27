import sys
import json
from collections import deque

class ProcessorState:
    def __init__(self):
        self.PC = 0
        self.PhysicalRegisterFile = [0] * 64
        self.DecodedPCs = []
        self.Exception = False
        self.ExceptionPC = 0
        self.RegisterMapTable = list(range(32))
        self.FreeList = deque(range(32, 64))
        self.BusyBitTable = [False] * 64
        self.ActiveList = []
        self.IntegerQueue = []
        self.ClockCycle = 0

    def to_dict(self):
        return {
            "PC": self.PC,
            "PhysicalRegisterFile": self.PhysicalRegisterFile,
            "DecodedPCs": self.DecodedPCs,
            "Exception": self.Exception,
            "ExceptionPC": self.ExceptionPC,
            "RegisterMapTable": self.RegisterMapTable,
            "FreeList": list(self.FreeList),
            "BusyBitTable": self.BusyBitTable,
            "ActiveList": [entry.to_dict() for entry in self.ActiveList],
            "IntegerQueue": [entry.to_dict() for entry in self.IntegerQueue],
            "ClockCycle": self.ClockCycle
        }

    class ActiveListEntry:
        def __init__(self, done, exception, logical_dest, old_dest, pc):
            self.Done = done
            self.Exception = exception
            self.LogicalDestination = logical_dest
            self.OldDestination = old_dest
            self.PC = pc

        def to_dict(self):
            return {
                "Done": self.Done,
                "Exception": self.Exception,
                "LogicalDestination": self.LogicalDestination,
                "OldDestination": self.OldDestination,
                "PC": self.PC
            }

    class IntegerQueueEntry:
        def __init__(self, dest_reg, opa_ready, opa_tag, opa_value, opb_ready, opb_tag, opb_value, opcode, pc):
            self.DestRegister = dest_reg
            self.OpAIsReady = opa_ready
            self.OpARegTag = opa_tag
            self.OpAValue = opa_value
            self.OpBIsReady = opb_ready
            self.OpBRegTag = opb_tag
            self.OpBValue = opb_value
            self.OpCode = opcode
            self.PC = pc

        def to_dict(self):
            return {
                "DestRegister": self.DestRegister,
                "OpAIsReady": self.OpAIsReady,
                "OpARegTag": self.OpARegTag,
                "OpAValue": self.OpAValue,
                "OpBIsReady": self.OpBIsReady,
                "OpBRegTag": self.OpBRegTag,
                "OpBValue": self.OpBValue,
                "OpCode": self.OpCode,
                "PC": self.PC
            }

def fetch_and_decode(state, instructions):
    num_instructions = min(4, len(instructions) - state.PC)
    for i in range(num_instructions):
        state.DecodedPCs.append(state.PC)
        state.PC += 1

def rename_and_dispatch(state, instructions):
    if len(state.FreeList) < len(state.DecodedPCs) or len(state.ActiveList) + len(state.DecodedPCs) > 32 or len(state.IntegerQueue) + len(state.DecodedPCs) > 32:
        return

    while state.DecodedPCs:
        pc = state.DecodedPCs.pop(0)
        instruction = instructions[pc].replace(',', '').split()  # Remove commas and split instruction
        opcode = instruction[0]
        dest = int(instruction[1][1:])  # Remove 'x' prefix and convert to int
        opA = int(instruction[2][1:]) if instruction[2][0] == 'x' else int(instruction[2])
        opB = int(instruction[3][1:]) if len(instruction) == 4 and instruction[3][0] == 'x' else int(instruction[3]) if len(instruction) == 4 else None

        new_phys_reg = state.FreeList.popleft()
        old_phys_reg = state.RegisterMapTable[dest]
        state.RegisterMapTable[dest] = new_phys_reg

        active_entry = ProcessorState.ActiveListEntry(done=False, exception=False, logical_dest=dest, old_dest=old_phys_reg, pc=pc)
        state.ActiveList.append(active_entry)

        if opcode == "addi":
            opB_ready = True
            opB_tag = None
            opB_value = opB
        else:
            opB_ready = state.BusyBitTable[opB] == False
            opB_tag = state.RegisterMapTable[opB]
            opB_value = state.PhysicalRegisterFile[opB] if opB_ready else None

        iq_entry = ProcessorState.IntegerQueueEntry(dest_reg=new_phys_reg,
                                                    opa_ready=state.BusyBitTable[opA] == False,
                                                    opa_tag=state.RegisterMapTable[opA],
                                                    opa_value=state.PhysicalRegisterFile[opA] if state.BusyBitTable[opA] == False else None,
                                                    opb_ready=opB_ready,
                                                    opb_tag=opB_tag,
                                                    opb_value=opB_value,
                                                    opcode=opcode,
                                                    pc=pc)
        state.IntegerQueue.append(iq_entry)
        state.BusyBitTable[new_phys_reg] = True

def issue(state):
    ready_instructions = [entry for entry in state.IntegerQueue if entry.OpAIsReady and entry.OpBIsReady]
    ready_instructions.sort(key=lambda x: x.PC)
    instructions_to_issue = ready_instructions[:4]

    for inst in instructions_to_issue:
        state.IntegerQueue.remove(inst)
        state.BusyBitTable[inst.DestRegister] = False
        for entry in state.ActiveList:
            if entry.PC == inst.PC:
                entry.Done = True

def commit(state):
    instructions_to_commit = []
    for entry in state.ActiveList:
        if entry.Done:
            instructions_to_commit.append(entry)
        if len(instructions_to_commit) == 4:
            break

    for entry in instructions_to_commit:
        state.ActiveList.remove(entry)
        state.FreeList.append(entry.OldDestination)
        state.BusyBitTable[entry.OldDestination] = False
        if entry.Exception:
            state.Exception = True
            state.ExceptionPC = entry.PC
            break

def exception_recovery(state):
    while state.ActiveList:
        entry = state.ActiveList.pop()
        state.RegisterMapTable[entry.LogicalDestination] = entry.OldDestination
        state.FreeList.appendleft(state.RegisterMapTable[entry.LogicalDestination])
        state.BusyBitTable[entry.OldDestination] = False
    state.PC = 0x10000
    state.Exception = False

def simulate(instructions):
    state = ProcessorState()
    log = []

    # Log the initial state
    log.append(state.to_dict())

    cycle_limit = 1000  # Set a reasonable cycle limit to prevent infinite loops

    while state.ClockCycle < cycle_limit:
        if not instructions and not state.ActiveList:
            break

        if state.Exception:
            exception_recovery(state)
        else:
            fetch_and_decode(state, instructions)
            rename_and_dispatch(state, instructions)
            issue(state)
            commit(state)

        state.ClockCycle += 1
        log.append(state.to_dict())

    return log

def main(input_path, output_path):
    with open(input_path, 'r') as f:
        instructions = json.load(f)

    log = simulate(instructions)

    with open(output_path, 'w') as f:
        json.dump(log, f, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python simulator.py input.json output.json")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    main(input_path, output_path)
