class start:
       def __init__(self):
              self.output_number_result = 0
              self.property_number_a = "0"
       def getValue(self, n):
              return n["properties"]["a"]
 
       def execute(self, params):
              pass

class addition:
       def __init__(self):
              self.input_number_a = 0
              self.input_number_b = 0
              self.output_number_result = 0

       def getValue(self, n):
              print("getValue  addition %d %d " % (int(self.input_number_a), int(self.input_number_b)))
              return int(self.input_number_a) + int(self.input_number_b)

       def execute(self, params):
              self.input_number_a = params[0]
              self.input_number_b = params[1]
              print("execute addition  %d %d " % (int(self.input_number_a),int(self.input_number_b)))

class integer:
       def __init__(self):
              self.output_int_result = 0
              self.property_number_a = "1"

       def getValue(self, n):
              return n["properties"]["a"]

       def execute(self, params):
              pass

class result:
       def __init__(self):
              self.input_int_result = 0
       def getValue(self, n):
              print( self.input_int_result )

       def execute(self, params):
              self.input_int_result = params
              return self.input_int_result
