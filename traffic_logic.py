import time

class TrafficLightController:
    """
    Manages the state of a single traffic light based on vehicle counts.
    """
    def __init__(self):
        self.state = "RED"  # Start as RED
        self.last_state_change_time = time.time()
        
        # --- Configuration ---
        self.GREEN_DURATION = 30  # Max green light time (seconds)
        self.RED_DURATION = 60    # Max red light time
        self.EMPTY_LANE_TIMEOUT = 5 # How long to wait for an empty green lane
        
        # This tracks the timer for an empty lane
        self.current_empty_lane_start_time = -1

    def get_state_color(self):
        """Returns the (B,G,R) color for the current state."""
        return (0, 255, 0) if self.state == "GREEN" else (0, 0, 255)

    def get_timer_display(self):
        """Returns the time remaining in the current state as a string."""
        elapsed = time.time() - self.last_state_change_time
        
        if self.state == "GREEN":
            # If we are in the "empty lane" countdown
            if self.current_empty_lane_start_time != -1:
                empty_elapsed = time.time() - self.current_empty_lane_start_time
                return max(0, int(self.EMPTY_LANE_TIMEOUT - empty_elapsed))
            # Otherwise, show the max green time
            return max(0, int(self.GREEN_DURATION - elapsed))
        else:
            # If red, timer counts down from max
            return max(0, int(self.RED_DURATION - elapsed))

    def update(self, vehicle_count):
        """
        This is the "brain". Call this on every frame.
        It updates the light's state based on the vehicle count.
        """
        current_time = time.time()
        elapsed_time = current_time - self.last_state_change_time
        
        # --- GREEN LIGHT LOGIC ---
        if self.state == "GREEN":
            if vehicle_count > 0:
                # Cars are present. Reset the "empty lane" timer.
                self.current_empty_lane_start_time = -1 
            
            if vehicle_count == 0 and self.current_empty_lane_start_time == -1:
                # Lane just became empty. Start a 5-second timer.
                self.current_empty_lane_start_time = current_time
            
            # Check if we should turn RED
            empty_timeout_lapsed = (self.current_empty_lane_start_time != -1 and (current_time - self.current_empty_lane_start_time) >= self.EMPTY_LANE_TIMEOUT)
            max_green_time_lapsed = (elapsed_time >= self.GREEN_DURATION)

            if empty_timeout_lapsed or max_green_time_lapsed:
                self.state = "RED"
                self.last_state_change_time = current_time
                self.current_empty_lane_start_time = -1
        
        # --- RED LIGHT LOGIC ---
        elif self.state == "RED":
            # Check if we should turn GREEN
            high_queue = (vehicle_count > 5) # Smart logic: big queue
            cycle_finished = (elapsed_time >= self.RED_DURATION) # Standard logic: timer finished
            
            if high_queue or cycle_finished:
                self.state = "GREEN"
                self.last_state_change_time = current_time
                self.current_empty_lane_start_time = -1 # Reset empty lane timer
# --- END OF CLASS ---