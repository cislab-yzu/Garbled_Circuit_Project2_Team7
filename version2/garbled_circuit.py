# Garbled Circuit
# python 3.7.4
# encoding=utf-8

import os.path
import random
import hashlib
import string
import time

class GC:
    # initial
    def __init__(self, plaintext, input_wire, output_wire, circuit):
        self.message = ""
        self._input_wire = [] # name of input line
        self._output_wire = [] # name of output line
        self._wire = dict() # name of line
        self.garbled_wire = dict() # garbled name of line
        self._circuit = [] # circuit description like verilog
        self.garbled_truth_table = [] # garbled truth table
        self.ans = dict()

        self.genTime = time.time()
        self.input_message(plaintext, input_wire, output_wire)
        self.input_circuit(circuit)
        self.generate_garbled_circuit()
        self.genTime = time.time() - self.genTime

    # execute
    def update(self):
        self.decTime = time.time()
        self.decrypt_garbled_circuit()
        self.decTime = time.time() - self.decTime

    # input message and wire
    def input_message(self, plaintext, input_wire, output_wire):
        self.message = plaintext
        self._input_wire = input_wire
        self._output_wire = output_wire

        if len(self.message) != len(self._input_wire):
            print("Input format error!", self.message, self._input_wire)
            exit(0)

        for c in self._input_wire:
            self._wire[c] = self.keygen()
        for c in self._output_wire:
            self._wire[c] = self.keygen()
        # print(self._wire)

    # circuit description
    def input_circuit(self, circuit):
        self._circuit = []
        for gate in circuit:
            gate_ = gate.split()
            if len(gate_) != 4:
                print("Gate format error!", gate_)
                exit(0)
            self.save_wire(gate_)
            circuit_ = [self._wire[w] for w in gate_[1:]]
            circuit_.insert(0, gate_[0])
            self._circuit.append(circuit_)

    # garbled all truth table
    def garble_gate(self, gate):
        gatetable = []
        for x in [0, 1]:
            for y in [0, 1]:
                s = self.garbled_wire[gate[1]][x] + self.garbled_wire[gate[2]][y]
                if gate[0] == "AND":
                    gatetable.append(self.get_md5hash(s + self.garbled_wire[gate[3]][int(x and y)]))
                elif gate[0]  == "NAND":
                    gatetable.append(self.get_md5hash(s + self.garbled_wire[gate[3]][int(not(x and y))]))
                elif gate[0]  == "OR":
                    gatetable.append(self.get_md5hash(s + self.garbled_wire[gate[3]][int(x or y)]))
                elif gate[0]  == "NOR":
                    gatetable.append(self.get_md5hash(s + self.garbled_wire[gate[3]][int(not(x or y))]))
                elif gate[0] == "XOR":
                    gatetable.append(self.get_md5hash(s + self.garbled_wire[gate[3]][int(x != y)]))
                elif gate[0] == "XNOR":
                    gatetable.append(self.get_md5hash(s + self.garbled_wire[gate[3]][int(not(x != y))]))
                else:
                    print(gate[0], "not found")
        random.shuffle(gatetable)
        return gatetable

    # generate garble circuit with random string and garbled truth table
    def generate_garbled_circuit(self):
        self.garble_wire()
        for key, gate in enumerate(self._circuit):
            table = self.garble_gate(gate)
            self.garbled_truth_table.append(table)
            self._circuit[key].pop(0)

    # random letters and digits generation
    def garble_wire(self):
        self.garbled_wire = dict()
        for c in self._wire.values():
            w = []
            w.append(self.keygen())
            w.append(self.keygen())
            self.garbled_wire[c] = w

    # save wire name
    def save_wire(self, gate):
        for w in gate[1:]:
            if (not w in self._wire.keys()):
                self._wire[w] = self.keygen()
        return 0

    # generate md5 hash value
    def get_md5hash(self, data):
        m = hashlib.md5()
        m.update(data.encode('utf-8'))
        return m.hexdigest()

    # generate random string
    def keygen(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    # find hash value in the truth table
    def find_table(self, md5hash, i):
        for key in self.garbled_truth_table[i]:
            if md5hash == key:
                return i, True
        return 0, False

    # execute garbled circuit
    def decrypt_garbled_circuit(self):
        wire = dict()
        for key, i in enumerate(self.message):
            wire[self._wire[self._input_wire[key]]] = self.garbled_wire[self._wire[self._input_wire[key]]][int(i)]
        for i, gate in enumerate(self._circuit):
            for s in self.garbled_wire[gate[2]]:
                answer = []
                md5hash = self.get_md5hash(wire[gate[0]] + wire[gate[1]] + s)
                answer = self.find_table(md5hash, i)
                if answer[1] == True:
                    wire[gate[2]] = s
                    break
        for w in self._output_wire:
            self.ans[w] = self.garbled_wire[self._wire[w]].index(wire[self._wire[w]])

def main():
    print("-Garbled Circuit-")
    input_wire = []
    output_wire = []
    circuit = []
    # os.chdir("D:/Development/Project7-2_Garbled_circuit/version2")
    if os.path.isfile("circuit/gc"):
        f = open("circuit/gc", "r")
        if f.mode == "r":
            lines = f.readlines()
            input_wire = lines.pop(0).split()
            output_wire = lines.pop(0).split()
            for line in lines:
                circuit.append(line)
        f.close()
    else:
        print("gc.txt not found")
        exit(0)

    plaintext = input("Input message:")
    if len(input_wire) == len(plaintext):
        gc_ = GC(plaintext, input_wire, output_wire, circuit)
        gc_.update()
        print("Garbled wire:")
        print(gc_.garbled_wire)
        print("Garbled truth table:")
        print(gc_.garbled_truth_table)
        print("Answer of decryption:")
        for key, i in gc_.ans.items():
            print(key, i)
    else:
        print("Input string length error!")
        exit(0)

# main function execution
if __name__ == "__main__":
    main()
