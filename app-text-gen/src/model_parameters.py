"""
Model parameter management for temperature, max_tokens, etc.
"""

class ModelParameters:
    """Class to manage model parameters"""
    
    def __init__(self):
        """Initialize with default parameters"""
        self.temperature = 0.7
        self.max_tokens = 500
        self.top_p = 1.0
        self.frequency_penalty = 0.0
        self.presence_penalty = 0.0
    
    def get_all_parameters(self):
        """Get all parameters as a dictionary"""
        return {
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty
        }
    
    def set_temperature(self, value):
        """Set temperature (0.0 to 2.0)"""
        try:
            temp = float(value)
            if 0.0 <= temp <= 2.0:
                self.temperature = temp
                return True, f"Temperature set to {temp}"
            else:
                return False, "Temperature must be between 0.0 and 2.0"
        except ValueError:
            return False, "Invalid temperature value"
    
    def set_max_tokens(self, value):
        """Set max tokens (1 to 4000)"""
        try:
            tokens = int(value)
            if 1 <= tokens <= 4000:
                self.max_tokens = tokens
                return True, f"Max tokens set to {tokens}"
            else:
                return False, "Max tokens must be between 1 and 4000"
        except ValueError:
            return False, "Invalid max tokens value"
    
    def set_top_p(self, value):
        """Set top_p / nucleus sampling (0.0 to 1.0)"""
        try:
            top_p = float(value)
            if 0.0 <= top_p <= 1.0:
                self.top_p = top_p
                return True, f"Top_p set to {top_p}"
            else:
                return False, "Top_p must be between 0.0 and 1.0"
        except ValueError:
            return False, "Invalid top_p value"
    
    def set_frequency_penalty(self, value):
        """Set frequency penalty (-2.0 to 2.0)"""
        try:
            penalty = float(value)
            if -2.0 <= penalty <= 2.0:
                self.frequency_penalty = penalty
                return True, f"Frequency penalty set to {penalty}"
            else:
                return False, "Frequency penalty must be between -2.0 and 2.0"
        except ValueError:
            return False, "Invalid frequency penalty value"
    
    def set_presence_penalty(self, value):
        """Set presence penalty (-2.0 to 2.0)"""
        try:
            penalty = float(value)
            if -2.0 <= penalty <= 2.0:
                self.presence_penalty = penalty
                return True, f"Presence penalty set to {penalty}"
            else:
                return False, "Presence penalty must be between -2.0 and 2.0"
        except ValueError:
            return False, "Invalid presence penalty value"
    
    def reset_to_defaults(self):
        """Reset all parameters to defaults"""
        self.temperature = 0.7
        self.max_tokens = 500
        self.top_p = 1.0
        self.frequency_penalty = 0.0
        self.presence_penalty = 0.0
        return True, "All parameters reset to defaults"
    
    def display_parameters(self):
        """Display current parameters"""
        print("\n" + "=" * 60)
        print("Current Model Parameters")
        print("=" * 60)
        print(f"Temperature:        {self.temperature}")
        print(f"  (0.0 = deterministic, 2.0 = very random)")
        print(f"  Current setting: ", end="")
        if self.temperature < 0.3:
            print("Very focused/deterministic")
        elif self.temperature < 0.7:
            print("Focused but creative")
        elif self.temperature < 1.2:
            print("Balanced (default)")
        else:
            print("Very creative/random")
        
        print(f"\nMax Tokens:         {self.max_tokens}")
        print(f"  (Maximum response length)")
        
        print(f"\nTop P (Nucleus):    {self.top_p}")
        print(f"  (Diversity of token selection, 1.0 = use all tokens)")
        
        print(f"\nFrequency Penalty:  {self.frequency_penalty}")
        print(f"  (-2.0 to 2.0, positive = reduce repetition)")
        
        print(f"\nPresence Penalty:   {self.presence_penalty}")
        print(f"  (-2.0 to 2.0, positive = encourage new topics)")
        
        print("=" * 60)
    
    def interactive_setup(self):
        """Interactive setup of parameters"""
        print("\n" + "=" * 60)
        print("Configure Model Parameters")
        print("=" * 60)
        
        print("\nTemperature (0.0-2.0, default: 0.7):")
        print("  - Use 0.0 for deterministic, focused responses")
        print("  - Use 0.7 for balanced creativity and focus")
        print("  - Use higher values (1.0+) for creative, random responses")
        temp_input = input("Enter temperature (or press Enter to keep current): ").strip()
        if temp_input:
            success, msg = self.set_temperature(temp_input)
            print(f"  {msg}")
        
        print("\nMax Tokens (1-4000, default: 500):")
        print("  - Controls maximum length of the response")
        tokens_input = input("Enter max tokens (or press Enter to keep current): ").strip()
        if tokens_input:
            success, msg = self.set_max_tokens(tokens_input)
            print(f"  {msg}")
        
        print("\nTop P (0.0-1.0, default: 1.0):")
        print("  - Controls diversity of response")
        print("  - Lower values = more focused")
        top_p_input = input("Enter top_p (or press Enter to keep current): ").strip()
        if top_p_input:
            success, msg = self.set_top_p(top_p_input)
            print(f"  {msg}")
        
        print("\nFrequency Penalty (-2.0 to 2.0, default: 0.0):")
        print("  - Positive values reduce repetition of tokens")
        freq_input = input("Enter frequency penalty (or press Enter to keep current): ").strip()
        if freq_input:
            success, msg = self.set_frequency_penalty(freq_input)
            print(f"  {msg}")
        
        print("\nPresence Penalty (-2.0 to 2.0, default: 0.0):")
        print("  - Positive values encourage new topics")
        pres_input = input("Enter presence penalty (or press Enter to keep current): ").strip()
        if pres_input:
            success, msg = self.set_presence_penalty(pres_input)
            print(f"  {msg}")

def display_parameter_presets():
    """Display common parameter presets"""
    print("\n" + "=" * 60)
    print("Parameter Presets")
    print("=" * 60)
    
    presets = {
        "1": {
            "name": "Precise/Analytical",
            "description": "For factual, deterministic responses",
            "params": {
                "temperature": 0.2,
                "max_tokens": 1000,
                "top_p": 0.95,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
        },
        "2": {
            "name": "Balanced (Default)",
            "description": "Good for general conversation",
            "params": {
                "temperature": 0.7,
                "max_tokens": 500,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
        },
        "3": {
            "name": "Creative",
            "description": "For creative writing and brainstorming",
            "params": {
                "temperature": 1.2,
                "max_tokens": 1500,
                "top_p": 0.9,
                "frequency_penalty": 0.5,
                "presence_penalty": 0.6
            }
        },
        "4": {
            "name": "Concise",
            "description": "For short, focused responses",
            "params": {
                "temperature": 0.5,
                "max_tokens": 200,
                "top_p": 0.95,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
        },
        "5": {
            "name": "Verbose",
            "description": "For detailed, comprehensive responses",
            "params": {
                "temperature": 0.8,
                "max_tokens": 3000,
                "top_p": 1.0,
                "frequency_penalty": 0.2,
                "presence_penalty": 0.2
            }
        }
    }
    
    for key, preset in presets.items():
        print(f"\n{key}. {preset['name']}")
        print(f"   {preset['description']}")
        params = preset['params']
        print(f"   Temp: {params['temperature']}, Tokens: {params['max_tokens']}, Top_p: {params['top_p']}")
    
    print("\n" + "=" * 60)
    
    return presets

def apply_preset(model_params, preset_key, presets):
    """Apply a preset to model parameters"""
    if preset_key in presets:
        preset = presets[preset_key]
        params = preset['params']
        
        model_params.temperature = params['temperature']
        model_params.max_tokens = params['max_tokens']
        model_params.top_p = params['top_p']
        model_params.frequency_penalty = params['frequency_penalty']
        model_params.presence_penalty = params['presence_penalty']
        
        return True, f"Applied preset: {preset['name']}"
    
    return False, "Invalid preset"

