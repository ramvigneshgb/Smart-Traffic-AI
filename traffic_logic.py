import time

class IntersectionController:
    """
    Manages a 4-way intersection. Ensures only one lane is GREEN at a time.
    NEW: Includes an Accident Response Protocol to shut down blocked lanes.
    """
    def __init__(self):
        self.states = {"North": "GREEN", "South": "RED", "East": "RED", "West": "RED"}
        self.queues = {"North": 0, "South": 0, "East": 0, "West": 0}
        self.accidents = {"North": False, "South": False, "East": False, "West": False}
        self.active_lane = "North"
        
        self.last_switch_time = time.time()
        self.empty_start_time = -1

        self.MIN_GREEN_DURATION = 10  
        self.MAX_GREEN_DURATION = 40  
        self.EMPTY_LANE_TIMEOUT = 4   

    def update(self, vehicle_counts: dict, accident_alerts: dict):
        self.queues = vehicle_counts
        self.accidents = accident_alerts
        current_time = time.time()
        elapsed_time = current_time - self.last_switch_time
        active_count = self.queues.get(self.active_lane, 0)

        # 🚨 ACCIDENT OVERRIDE LOGIC 🚨
        for lane, has_accident in self.accidents.items():
            if has_accident:
                self.states[lane] = "BLOCKED"

        # If an accident happens in the currently active green lane, shut it down instantly
        if self.accidents.get(self.active_lane, False):
            self._switch_to_highest_queue(current_time)
            return # Exit early

        # Standard Empty Lane Tracking
        if active_count == 0 and self.empty_start_time == -1:
            self.empty_start_time = current_time
        elif active_count > 0:
            self.empty_start_time = -1

        force_switch = False
        
        if elapsed_time >= self.MAX_GREEN_DURATION:
            force_switch = True
        elif elapsed_time >= self.MIN_GREEN_DURATION and self.empty_start_time != -1:
            if (current_time - self.empty_start_time) >= self.EMPTY_LANE_TIMEOUT:
                force_switch = True

        if force_switch:
            self._switch_to_highest_queue(current_time)

    def _switch_to_highest_queue(self, current_time):
        best_lane = None
        max_queue = -1
        
        for lane, count in self.queues.items():
            # Skip the active lane AND skip any lane with an accident
            if lane != self.active_lane and not self.accidents[lane]:
                if count > max_queue:
                    max_queue = count
                    best_lane = lane

        if max_queue > 0 and best_lane is not None:
            # Change old lane to RED (unless it was blocked by an accident)
            if self.states[self.active_lane] != "BLOCKED":
                self.states[self.active_lane] = "RED"
                
            self.active_lane = best_lane
            self.states[self.active_lane] = "GREEN"
            self.last_switch_time = current_time
            self.empty_start_time = -1

    def get_state_color(self, lane):
        if self.states[lane] == "GREEN":
            return (0, 255, 0)
        elif self.states[lane] == "BLOCKED":
            return (0, 165, 255) # Orange for Accidents
        else:
            return (0, 0, 255) # Red

    def get_timer_display(self):
        return int(time.time() - self.last_switch_time)