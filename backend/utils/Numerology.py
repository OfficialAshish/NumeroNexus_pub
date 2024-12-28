
import json
from backend.utils.data.planes_data import *
from backend.utils.data.planet_data import *
from backend.utils.data.compatibility_data import *
# from data.planes_data import *
# from data.planet_data import *
# from data.compatibility_data import *
 
from datetime import datetime

# Helper function to validate the Date of Birth
def validate_dob(dob):
    try:
        date_obj = datetime.strptime(dob, "%Y-%m-%d")  # Ensure the correct format
        current_year = datetime.now().year
        if not (1900 <= date_obj.year <= current_year):
            raise ValueError(f"Year must be between 1900 and {current_year}.")
        return date_obj.day, date_obj.month, date_obj.year
    except ValueError as e:
        raise ValueError(f"Invalid dob: {dob}. Error: {str(e)}")

# Function to calculate Mulank (Psychic Number) and optionally Bhagyank (Destiny Number)
def calc_mulank(dob, bhagyank_also=False):
    # Validate and split the date
    dd, mm, yy = validate_dob(dob)
        
    def get_digit_sum(num):
        while num > 9:
            num = sum(map(int, str(num)))
        return num
        
    mulank = get_digit_sum(dd)
    
    if not bhagyank_also:
        return mulank
    
    bhagyank = get_digit_sum(mulank + get_digit_sum(mm) + get_digit_sum(yy))
    return mulank, bhagyank

# print( mulank("27-04-2001",True))   
# print( calc_mulank("28-7-1985",True))   

# Person class to hold individual numerology details
class Person():
    def __init__(self, dob:str, gender:str, name="Unnamed"):
        self.name = name
        self.dob = dob
        self.gender = gender
        self.init_calc()
        
    def __str__(self):
        lo_shu_grid_str = self.print_loshu_grid() if self.loshu_grid else "Grid not generated yet"
        return (f"Person: {self.name}\nDOB: {self.dob}\nGender: {self.gender}\n"
                f"Mulank: {self.mulank}\nBhagyank: {self.bhagyank}\n"
                f"Kua Number: {self.kua_num}\nLo Shu Magic Square Grid:\n{lo_shu_grid_str}")

    def init_calc(self):
        self.mulank , self.bhagyank = calc_mulank(self.dob, bhagyank_also = True)
        self.kua_num = self.calc_kua_num()
        self.namaank = self.calc_namaank()

        self.loshu_grid = None
        self.make_loshu_grid()
        
        self.find_lucky_numbers()
        self.standard_planes = None
        # self.calculate_identity_planes()
    
    def calc_namaank(self):
        if self.name == "Unnamed":
            return 0
        self.std_chaldean = {
            1: ['A', 'I', 'J', 'Q', 'Y'],
            2: ['B', 'K', 'R'],
            3: ['C', 'G', 'L', 'S'],
            4: ['D', 'M', 'T'],
            5: ['E', 'H', 'N', 'X'],
            6: ['U', 'V', 'W'],
            7: ['O', 'Z'],
            8: ['F', 'P']
        }
        total = 0
        name_upper = self.name.upper()   

        for char in name_upper:
            for num, letters in self.std_chaldean.items():
                if char in letters:
                    total += num
                    break  # Exit loop once found

        while total > 9:
            total = sum(int(digit) for digit in str(total))
        return total
    
    def calc_kua_num(self):
        """ not considering it,influences only 20% or less """
        return 0
        if self.gender is None :
            raise ValueError("gender must be specified")
        if self.gender == "male" :
            self.kua_number = 11 - self.bhagyank
        else :
            self.kua_number = 4 + self.bhagyank
        return self.kua_number
        
    def find_lucky_numbers(self):
        """ 
        Find lucky numbers based on Mulank and Bhagyank compatibility
        """
        key1, key2 = self.mulank, self.bhagyank
        data = planets_compatibility
        enemies1 = [int(enemy) for enemy in data[key1]["enemies"].split(",")]
        neutral1 = [int(neutral) for neutral in data[key1]["neutral"].split(",")]
        enemies2 = [int(enemy) for enemy in data[key2]["enemies"].split(",")]
        neutral2 = [int(neutral) for neutral in data[key2]["neutral"].split(",")]

        enemies_sum = set(enemies1 + enemies2)
        neutral_sum = set(neutral1 + neutral2)
        # neutral_sum = set([map(int, data[key1]["neutral"].split(",")) + map(int, data[key2]["neutral"].split(","))])

        self.lucky_numbers = [str(num) for num in range(1, 10) if num not in enemies_sum.union(neutral_sum)]

        return self.lucky_numbers
    
    def make_loshu_grid(self):
        # Generate the Lo Shu Grid based on DOB and other numbers        
        self.std_l_s_grid = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
        dob_numbers = list(map(int, self.dob.replace('-', ''))) + [self.mulank, self.bhagyank, self.kua_num, self.namaank]
        # print(dob_numbers)
        # Count the occurrences of numbers in the standard grid
        self.planes_num_count = [[0] * 3 for _ in range(3)]
        std_position = {4: (0, 0), 9: (0, 1), 2: (0, 2), 3: (1, 0), 5: (1, 1), 7: (1, 2), 8: (2, 0), 1: (2, 1), 6: (2, 2)}
        
        for num in dob_numbers:
            if num in std_position:
                i, j = std_position[num]
                self.planes_num_count[i][j] += 1
        
        # print(self.planes_num_count)

        # Create the Lo Shu grid
        self.loshu_grid = [[[] for _ in range(3)] for _ in range(3)]
        for num, (i, j) in std_position.items():
            self.loshu_grid[i][j] = [num] * self.planes_num_count[i][j]
        
        # print("Grid:", self.loshu_grid)
    
        
    def print_loshu_grid(self):
        """Returns the Lo Shu Magic Square grid str """
        return "\n".join(" ".join(map(str, row)) for row in self.loshu_grid)
      
 
    def calculate_identity_planes(self):
        self.standard_planes = {
            'Mind': (4, 9, 2),
            'Heart': (3, 5, 7),
            'Practical': (8, 1, 6),
            'Vision': (4, 3, 8),
            'Will': (9, 5, 1),
            'Action': (2, 7, 6),
        }
        # percentage of plane completion
        planes_percent = {1:"30%", 2:"70%", 3:"100%"}
        
        planes_tf = [[int(self.planes_num_count[i][j] != 0) for j in range(3)] for i in range(3)]
        # print(planes_tf)
        
        # Mind, Heart, Practical planes (horizontal)
        mind_tup = tuple(planes_tf[0])
        heart_tup = tuple(planes_tf[1])
        practical_tup = tuple(planes_tf[2])
        
        mind_data = mind_plane_data.get(mind_tup, {}).copy()
        heart_data = heart_plane_data.get(heart_tup, {}).copy()
        practical_data = practical_plane_data.get(practical_tup, {}).copy()
    
        mind_data["completion"] =  planes_percent.get(mind_tup.count(1) , "0%")
        heart_data["completion"] =  planes_percent.get(heart_tup.count(1) , "0%")
        # print("debug",practical_data, practical_tup)
        practical_data["completion"] =  planes_percent.get(practical_tup.count(1) , "0%")
        
        # print(mind_data,heart_data,practical_data)
        
        # Vision, Will, Action planes (vertical)
        vision_tup = tuple([planes_tf[i][0] for i in range(3)])
        will_tup = tuple([planes_tf[i][1] for i in range(3)])
        action_tup = tuple([planes_tf[i][2] for i in range(3)])

        vision_data = vision_plane_data.get(vision_tup, {}).copy()
        will_data = will_plane_data.get(will_tup, {}).copy()
        action_data = action_plane_data.get(action_tup, {}).copy()
    
        vision_data["completion"] =  planes_percent.get(vision_tup.count(1) , "0%")
        will_data["completion"] =  planes_percent.get(will_tup.count(1) , "0%")
        action_data["completion"] =  planes_percent.get(action_tup.count(1) , "0%")
        
        # print(vision_data, will_data, action_data)
        
        # Now diagonal planes (Rajyog)
        self.rajyog_data_list = []
        if planes_tf[2][0] == 1 and planes_tf[2][1] == 1 and planes_tf[2][2] == 1 :
            self.rajyog_data_list.append(rajyog_data.get((8,1,6)))
            
        if planes_tf[1][1] == 1 :
            if planes_tf[0][0] == 1 and planes_tf[2][2] == 1 :
                # (2,5,8)
                self.rajyog_data_list.append(rajyog_data.get((2,5,8)))
            if planes_tf[0][2] == 1 and planes_tf[2][0] == 1 :
                # (4,5,6)
                self.rajyog_data_list.append(rajyog_data.get((4,5,6)))
                
        # print(self.rajyog_data_list)
         
        # print("Standard Grid:")
        # for row in self.std_l_s_grid:
        #     print("  ".join(str(col) for col in row ))
        # print()
        
        # print("Your Lo Shu Grid:")
        # print(self.print_loshu_grid())
         
        # Define plane categories
        self.planes_categories = ["Mind", "Heart", "Practical", "Vision", "Will", "Action"]
        self.planes_tuples = {
            'Mind': mind_tup,
            'Heart': heart_tup,
            'Practical': practical_tup,
            'Vision': vision_tup,
            'Will': will_tup,
            'Action': action_tup,
        }
        self.all_planes_data = {
            'Mind': mind_data,
            'Heart': heart_data,
            'Practical': practical_data,
            'Vision': vision_data,
            'Will': will_data,
            'Action': action_data,
        } 


    # MATHCHING
    def calculate_compatibility(self, other):
        """Calculate compatibility score between two individuals."""
        if not isinstance(other, Person):
            raise ValueError("Compatibility can only be calculated between two Person objects.")

        score = 0

        # Step 1: Mulank Compatibility
        score += self.mulank_compatibility(other)

        # Step 2: Incoming and Outgoing Numbers
        score += self.count_unique_grid_numbers(other)

        # Step 3: Plane Completion
        combined_grid = self.combine_grids(other)
        score += self.evaluate_plane_completion(combined_grid)

        # Step 4: Presence of Rajyog
        score += self.check_rajyog_in_combined_grid(combined_grid)

        # Step 5: Presence of Numbers 5 and 6
        score += self.check_presence_of_5_and_6(combined_grid)

        return score

    def mulank_compatibility(self, other):
        """Assess compatibility based on Mulank."""
        key1, key2 = self.mulank, other.mulank
        compatibility = planets_compatibility[key1]

        if str(key2) in compatibility["friends"]:
            return 5  # Friendly Mulank match
        elif str(key2) in compatibility["neutral"]:
            return 3  # Neutral Mulank match
        elif str(key2) in compatibility["enemies"]:
            return -5  # Enemy Mulank match
        return 0

    def count_unique_grid_numbers(self, other):
        """Counts unique numbers present in one grid but not the other."""
        own_numbers = set(self.flatten_grid(self.loshu_grid))
        other_numbers = set(self.flatten_grid(other.loshu_grid))

        unique_in_one = own_numbers.symmetric_difference(other_numbers)
        return 2 * len(unique_in_one)  # 2 points for each unique number

    def evaluate_plane_completion(self, combined_grid):
        """Evaluate the completion of all standard planes in the combined Lo Shu grid."""
        score = 0
        completed_planes = []  # To keep track of which planes are completed

        # Flatten the combined grid to check for the presence of plane numbers
        flattened_grid = set(self.flatten_grid(combined_grid))

        # Iterate through the planes and check for complete planes
        for plane, numbers in self.standard_planes.items():
            if all(num in flattened_grid for num in numbers):
                score += 2  # 2 points for each complete plane
                completed_planes.append(plane)  # Track the completed plane

        return completed_planes, score  # Return the list of completed planes and score


    def combine_grids(self, other):
        """Combine two Lo Shu grids into one, ensuring unique values in each cell."""
        combined_grid = [[[] for _ in range(3)] for _ in range(3)]

        # Merge two grids cell by cell 
        for i in range(3):
            for j in range(3):
                combined_values = list(self.loshu_grid[i][j] + other.loshu_grid[i][j])
                combined_grid[i][j] = combined_values[:3]  # Limit to max 3 numbers per cell

        return combined_grid  # Return the combined Lo Shu grid


    def check_rajyog_in_combined_grid(self, combined_grid):
        """Check for Rajyog patterns in the combined Lo Shu grid."""
        rajyog_patterns = {
            "Wealth Rajyog": (8, 1, 6),
            "Prosperity Rajyog": (2, 5, 8),
            "Success Rajyog": (4, 5, 6)
        }
        flattened_grid = set(self.flatten_grid(combined_grid))

        found_rajyogs = []  # To track which Rajyog patterns are found
        for rajyog_name, pattern in rajyog_patterns.items():
            if all(num in flattened_grid for num in pattern):
                found_rajyogs.append(rajyog_name)  # Track the found Rajyog pattern

        return found_rajyogs  # Return the list of found Rajyogs


    def flatten_grid(self, grid):
        """Flatten a 3x3 Lo Shu grid into a 1D list of numbers."""
        return [num for row in grid for cell in row for num in cell]


    def check_presence_of_5_and_6(self, combined_grid):
        """Check for the presence of numbers 5 and 6 in the combined grid."""
        flattened_grid = set(self.flatten_grid(combined_grid))

        if 5 in flattened_grid :
            if 6 in flattened_grid:
                return 4
            return 2  
        return 0
    
    
    def calculate_compatibility_percentage(self, other):
        """Calculate the compatibility between two persons as a percentage."""
        
        # Step 1: Calculate Mulank Compatibility
        mulank_score = self.mulank_compatibility(other)

        # Step 2: Combine Lo Shu Grids and calculate incoming/outgoing numbers
        combined_grid = self.combine_grids(other)
        incoming_outgoing_score = self.count_unique_grid_numbers(other)

        # Step 3: Evaluate plane completion in the combined grid
        plane_completion_score = self.evaluate_plane_completion(combined_grid)

        # Step 4: Check for Rajyog patterns in the combined grid
        rajyog_score = self.check_rajyog_in_combined_grid(combined_grid)

        # Step 5: Check for the presence of numbers 5 and 6
        special_numbers_score = self.check_presence_of_5_and_6(combined_grid)

        # Calculate the total score
        total_score = (
            mulank_score
            + incoming_outgoing_score
            + plane_completion_score
            + rajyog_score
            + special_numbers_score
        )

        # Maximum possible score
        max_score = 5 + 18 + 12 + 6 + 4  # Mulank + Incoming/Outgoing + Planes + Rajyog + Special Numbers

        # Calculate compatibility percentage
        compatibility_percentage = (total_score / max_score) * 100

        return round(compatibility_percentage, 2)


# ------------------  for compatibility, implementing it in client side,,  ---------------
    def get_compatibility_details_json(self, other):
        if not self.standard_planes :
            self.calculate_identity_planes()
        """Return detailed matching compatibility data in JSON format."""

        # Step 1: Mulank Compatibility
        mulank_score = self.mulank_compatibility(other)
        mulank_status = (
            "Friendly" if mulank_score == 5 
            else "Neutral" if mulank_score == 3 
            else "Enemy" if mulank_score == -5 
            else "No Relationship"
        )

        # Step 2: Incoming and Outgoing Unique Numbers
        flattened_self = set(self.flatten_grid(self.loshu_grid))
        flattened_other = set(self.flatten_grid(other.loshu_grid))
        unique_to_self = flattened_self - flattened_other
        unique_to_other = flattened_other - flattened_self
        incoming_outgoing_score = 2 * (len(unique_to_self) + len(unique_to_other))

        # Step 3: Combine Lo Shu Grids and Evaluate Planes
        combined_grid = self.combine_grids(other)
        completed_planes, plane_completion_score = self.evaluate_plane_completion(combined_grid)

        # Step 4: Check for Rajyog patterns in the combined grid
        rajyog_planes = self.check_rajyog_in_combined_grid(combined_grid)
        rajyog_score = len(rajyog_planes) * 2

        # Step 5: Check for the presence of numbers 5 and 6
        special_numbers_present = [num for num in [5, 6] if num in self.flatten_grid(combined_grid)]
        special_numbers_score = len(special_numbers_present) * 2

        # Total Score and Max Score for Compatibility Percentage
        total_score = (
            mulank_score + incoming_outgoing_score +
            plane_completion_score + rajyog_score + special_numbers_score
        )
        max_score = 5 + 18 + 12 + 6 + 2
        compatibility_percentage = round((total_score / max_score) * 100, 2)

        # Prepare JSON data
        compatibility_data = {
            "mulank": {
                "person1_mulank": self.mulank,
                "person2_mulank": other.mulank,
                "status": mulank_status,
                "score": mulank_score
            },
            "unique_numbers": {
                "unique_to_person1": list(unique_to_self),
                "unique_to_person2": list(unique_to_other),
                "score": incoming_outgoing_score
            },
            "planes": {
                "completed_planes": completed_planes,
                "score": plane_completion_score
            },
            "rajyog": {
                "planes_found": rajyog_planes,
                "score": rajyog_score
            },
            "special_numbers": {
                "present": special_numbers_present,
                "score": special_numbers_score
            },
            "grids": {
                "person1_grid": self.loshu_grid,
                "person2_grid": other.loshu_grid,
                "combined_grid": combined_grid
            },
            "compatibility_percentage": compatibility_percentage
        }

        # Return the data as JSON
        return json.dumps(compatibility_data)
    
    
    def compatibility_data_json(self, other):
        """Compatibility data between two persons ."""
        
        # Step 1: Calculate Mulank Compatibility
        mulank_score = self.mulank_compatibility(other)

        # # Step 2: Combine Lo Shu Grids and calculate incoming/outgoing numbers
        # combined_grid = self.combine_grids(other)
        
         # Step 1: Mulank Compatibility
        mulank_score = self.mulank_compatibility(other)
        mulank_status = (
            "Friendly" if mulank_score == 5 
            else "Neutral" if mulank_score == 3 
            else "Enemy" if mulank_score == -5 
            else "No Relationship"
        )
        
        # Prepare JSON data
        compatibility_data = {
            "mulank": {
                "person1Mulank": self.mulank,
                "person2Mulank": other.mulank,
                "status": mulank_status,
                "score": mulank_score
            },
            "grids": {
                "person1Grid": self.loshu_grid,
                "person2Grid": other.loshu_grid,
                # "combineGrid": combined_grid
            }
        }

        # Return the data as JSON
        return json.dumps(compatibility_data )




# ------------------  for compatibility, implementing it in client side,,  ---------------
    def get_compatibility_details_json(self, other):
        if not self.standard_planes :
            self.calculate_identity_planes()
        """Return detailed matching compatibility data in JSON format."""

        # Step 1: Mulank Compatibility
        mulank_score = self.mulank_compatibility(other)
        mulank_status = (
            "Friendly" if mulank_score == 5 
            else "Neutral" if mulank_score == 3 
            else "Enemy" if mulank_score == -5 
            else "No Relationship"
        )

        # Step 2: Incoming and Outgoing Unique Numbers
        flattened_self = set(self.flatten_grid(self.loshu_grid))
        flattened_other = set(self.flatten_grid(other.loshu_grid))
        unique_to_self = flattened_self - flattened_other
        unique_to_other = flattened_other - flattened_self
        incoming_outgoing_score = 2 * (len(unique_to_self) + len(unique_to_other))

        # Step 3: Combine Lo Shu Grids and Evaluate Planes
        combined_grid = self.combine_grids(other)
        completed_planes, plane_completion_score = self.evaluate_plane_completion(combined_grid)

        # Step 4: Check for Rajyog patterns in the combined grid
        rajyog_planes = self.check_rajyog_in_combined_grid(combined_grid)
        rajyog_score = len(rajyog_planes) * 2

        # Step 5: Check for the presence of numbers 5 and 6
        special_numbers_present = [num for num in [5, 6] if num in self.flatten_grid(combined_grid)]
        special_numbers_score = len(special_numbers_present) * 2

        # Total Score and Max Score for Compatibility Percentage
        total_score = (
            mulank_score + incoming_outgoing_score +
            plane_completion_score + rajyog_score + special_numbers_score
        )
        max_score = 5 + 18 + 12 + 6 + 2
        compatibility_percentage = round((total_score / max_score) * 100, 2)

        # Prepare JSON data
        compatibility_data = {
            "mulank": {
                "person1_mulank": self.mulank,
                "person2_mulank": other.mulank,
                "status": mulank_status,
                "score": mulank_score
            },
            "unique_numbers": {
                "unique_to_person1": list(unique_to_self),
                "unique_to_person2": list(unique_to_other),
                "score": incoming_outgoing_score
            },
            "planes": {
                "completed_planes": completed_planes,
                "score": plane_completion_score
            },
            "rajyog": {
                "planes_found": rajyog_planes,
                "score": rajyog_score
            },
            "special_numbers": {
                "present": special_numbers_present,
                "score": special_numbers_score
            },
            "grids": {
                "person1_grid": self.loshu_grid,
                "person2_grid": other.loshu_grid,
                "combined_grid": combined_grid
            },
            "compatibility_percentage": compatibility_percentage
        }

        # Return the data as JSON
        return json.dumps(compatibility_data)




    
    # -----printing.......
    
    def get_overall_personality(self):
        st = "\nYour Overall Behaviour & Personality:\n"

        mulank, bhagyank = self.mulank, self.bhagyank
        st += f"\nMulank: {mulank} | Planet: {planet_names[mulank]}:\n"
        
        # Get mulank quality data
        mulank_data = mulank_quality_det.get(mulank, {})
        if mulank_data:
            st += f"Quality: {', '.join(mulank_data.get('quality', []))}\n"
            st += f"Personality: {mulank_data.get('personality', 'No personality information available.')}\n"
            st += f"Career: {mulank_data.get('career', 'No career information available.')}\n"
            st += f"Remedies: {', '.join(mulank_data.get('remedy', []))}\n"
        else:
            st += "No details available for this Mulank.\n"

        st += f"\nBhagyank: {bhagyank} | Planet: {planet_names[bhagyank]}:\n"
        
        # Get bhagyank quality data
        bhagyank_data = bhagyank_quality.get(bhagyank, {})
        if bhagyank_data:
            st += f"Quality: {bhagyank_data.get('quality', 'No quality information available.')}\n"
        else:
            st += "No details available for this Bhagyank.\n"

        # Compatibility
        m_b_data = m_b_compatibility.get((mulank, bhagyank), 'No specific compatibility found')
        st += f"\nCompatibility: {m_b_data}\n"

        print(st)
        return st
    
          
    def get_planes_data(self):
        # Append Rajyog data if available
        prt = "\n"
        if hasattr(self, "rajyog_data_list") and self.rajyog_data_list :
            # prt = "\nRajyog :\n" if self.rajyog_data_list else "\n"
            for raj_data in self.rajyog_data_list:
                prt += ("Rajyog:" + raj_data["rajyog"])
                prt += ("\nCompletion:" + raj_data["elements"])
                prt += ("\nQualities:" + ", ".join(raj_data["qualities"])) 
        prt += "\n"
                
        # Function to format plane data str
        def format_plane_data(plane_name, plane_data):
            std_pln_tuple = self.standard_planes.get(plane_name)
            tp = [i * j for i, j in zip(std_pln_tuple, self.planes_tuples[plane_name])]
            
            return (
                f"\nYour {plane_name} Plane {std_pln_tuple} :: "
                f"\nCompletion: {plane_data['completion']} i.e : {tp}"
                f"\nQualities: {', '.join(plane_data['qualities'])}\n"
            )

        # Printing plane data for Mind, Heart, Practical planes and all 
        prt += "\n".join(
            format_plane_data(category, self.all_planes_data[category])
            for category in self.planes_categories
        )
        
        # print(prt)
        return prt
        
    def to_str(self) -> str:
        if not self.standard_planes :
            self.calculate_identity_planes()
        return (
            f"{whats_numerology}\n\n"
            f"Person: {self.name}\nDOB: {self.dob}\nGender: {self.gender}\nMulank: {self.mulank}\nBhagyank: {self.bhagyank}\n"
            f"Lucky numbers: {self.lucky_numbers}\n\n"
            "Standard Lo Shu Magic Square Grid:\n"
            + "\n".join("  ".join(map(str, row)) for row in self.std_l_s_grid)
            + "\n\nYour Lo Shu Magic Square Grid:\n"
            + "\n".join("  ".join(map(str, row)) for row in self.loshu_grid)
            + "\n\n" + self.get_overall_personality()
            + "\n" + self.get_planes_data()
            + "\nDone!\n"
        )

    def save_txt(self, filename: str):
        with open(filename, 'w') as f:
            f.write(self.to_str())


    def to_json(self):
        if not self.standard_planes :
            self.calculate_identity_planes()
        # Prepare the data structure
        data = {
            "person_info": {
                "name": self.name,
                "dob": self.dob,
                "gender": self.gender,
                "namaank":self.namaank,
                "mulank": self.mulank,
                "bhagyank": self.bhagyank,
                "lucky_numbers": self.lucky_numbers,
            },
            "loshu_grid": self.loshu_grid,
            "overall_personality": {
                "mulank": {
                    "mulank_number": self.mulank,
                    "planet": planet_names[self.mulank],
                    "quality": mulank_quality_det.get(self.mulank, {}).get('quality', []),
                    "personality": mulank_quality_det.get(self.mulank, {}).get('personality', 'No personality information available.'),
                    "career": mulank_quality_det.get(self.mulank, {}).get('career', 'No career information available.'),
                    "remedies": mulank_quality_det.get(self.mulank, {}).get('remedy', [])
                },
                "bhagyank": {
                    "bhagyank_number": self.bhagyank,
                    "planet": planet_names[self.bhagyank],
                    "quality": bhagyank_quality.get(self.bhagyank, {}).get('quality', 'No quality information available.')
                },
                "compatibility": m_b_compatibility.get((self.mulank, self.bhagyank), 'No specific compatibility found')
            },
            "planes_data": {
                "planes": [
                    {
                        "plane_name": category,
                        "plane_tuple": self.planes_tuples.get(category),
                        "completion": self.all_planes_data[category]['completion'],
                        "qualities": self.all_planes_data[category]['qualities']
                    } for category in self.planes_categories
                ],
                "rajyog": [
                    {
                        "rajyog": rajyog["rajyog"],
                        "completion": rajyog["elements"],
                        "qualities": rajyog["qualities"]
                    } for rajyog in self.rajyog_data_list
                ] if hasattr(self, "rajyog_data_list") and self.rajyog_data_list else []
            }
        }
        # return data
        # Return JSON response
        return json.dumps(data)
        # return json.dumps(data, indent=1)

 
if __name__ == "__main__":
    # pass
 
    # ash = Person("27-4-2001","male","Ashish")
    # json_data = ash.to_json()
    # print(json_data)
    # ash.save_txt("Ashish.txt")
    person1 = Person(dob="1990-04-12", gender="male", name="John")
    person2 = Person(dob="1985-08-23", gender="female", name="Jane")
    # print(person1.get_compatibility_details_json(person2))
    print(person1.compatibility_data_json(person2))

    # compatibility_score = person1.calculate_compatibility(person2)
    # print(f"Compatibility Score: {compatibility_score}")

   