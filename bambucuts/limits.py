"""
Printer limits validation and safety system.

This module provides validation of G-code and movement commands against
printer boundaries to prevent hardware damage and unsafe operations.
"""

from typing import Optional, Tuple, List, Dict
import logging
import re

logger = logging.getLogger(__name__)


class PrinterLimits:
    """
    Validates movements against printer boundaries.
    
    Tracks current position and validates both absolute and relative moves
    to ensure they stay within printer bounds with optional safety margins.
    """
    
    def __init__(self, model_specs: Dict, enable_limits: bool = True, safety_margin: float = 5.0):
        """
        Initialize limits validator.
        
        Args:
            model_specs: Dictionary with printer model specifications
            enable_limits: Enable/disable limit checking
            safety_margin: Distance in mm from boundaries to maintain (safety buffer)
        """
        self.specs = model_specs
        self.enable_limits = enable_limits
        self.safety_margin = max(0, safety_margin)
        
        self.current_pos = {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
        
        self._update_safe_boundaries()
    
    def _update_safe_boundaries(self):
        """Calculate safe boundaries accounting for safety margin."""
        self.safe_x_min = self.specs['x_min'] + self.safety_margin
        self.safe_x_max = self.specs['x_max'] - self.safety_margin
        self.safe_y_min = self.specs['y_min'] + self.safety_margin
        self.safe_y_max = self.specs['y_max'] - self.safety_margin
        self.safe_z_min = self.specs['z_min'] + self.safety_margin
        self.safe_z_max = self.specs['z_max'] - self.safety_margin
    
    def set_safety_margin(self, margin: float):
        """Update safety margin and recalculate boundaries."""
        self.safety_margin = max(0, margin)
        self._update_safe_boundaries()
    
    def update_position(self, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None):
        """Update current position tracking."""
        if x is not None:
            self.current_pos['x'] = x
        if y is not None:
            self.current_pos['y'] = y
        if z is not None:
            self.current_pos['z'] = z
    
    def validate_absolute_move(self, x: Optional[float] = None, y: Optional[float] = None, 
                              z: Optional[float] = None) -> Tuple[bool, List[str]]:
        """Check if absolute move is within limits."""
        if not self.enable_limits:
            return True, []
        
        errors = []
        
        if x is not None:
            if not (self.specs['x_min'] <= x <= self.specs['x_max']):
                errors.append(f"X={x:.2f} exceeds printer limits [{self.specs['x_min']}, {self.specs['x_max']}]")
            elif not (self.safe_x_min <= x <= self.safe_x_max):
                errors.append(f"X={x:.2f} exceeds safe zone [{self.safe_x_min:.2f}, {self.safe_x_max:.2f}]")
        
        if y is not None:
            if not (self.specs['y_min'] <= y <= self.specs['y_max']):
                errors.append(f"Y={y:.2f} exceeds printer limits [{self.specs['y_min']}, {self.specs['y_max']}]")
            elif not (self.safe_y_min <= y <= self.safe_y_max):
                errors.append(f"Y={y:.2f} exceeds safe zone [{self.safe_y_min:.2f}, {self.safe_y_max:.2f}]")
        
        if z is not None:
            if not (self.specs['z_min'] <= z <= self.specs['z_max']):
                errors.append(f"Z={z:.2f} exceeds printer limits [{self.specs['z_min']}, {self.specs['z_max']}]")
            elif not (self.safe_z_min <= z <= self.safe_z_max):
                errors.append(f"Z={z:.2f} exceeds safe zone [{self.safe_z_min:.2f}, {self.safe_z_max:.2f}]")
        
        return len(errors) == 0, errors
    
    def validate_relative_move(self, dx: Optional[float] = None, dy: Optional[float] = None, 
                              dz: Optional[float] = None) -> Tuple[bool, List[str]]:
        """Check if relative move keeps position within limits."""
        new_x = self.current_pos['x'] + (dx or 0)
        new_y = self.current_pos['y'] + (dy or 0)
        new_z = self.current_pos['z'] + (dz or 0)
        
        return self.validate_absolute_move(new_x, new_y, new_z)
    
    def validate_gcode_line(self, gcode_line: str) -> Tuple[bool, List[str]]:
        """Validate a single G-code line for limit violations."""
        if not self.enable_limits:
            return True, []
        
        errors = []
        
        x_match = re.search(r'X([+-]?\d*\.?\d+)', gcode_line, re.IGNORECASE)
        y_match = re.search(r'Y([+-]?\d*\.?\d+)', gcode_line, re.IGNORECASE)
        z_match = re.search(r'Z([+-]?\d*\.?\d+)', gcode_line, re.IGNORECASE)
        
        x = float(x_match.group(1)) if x_match else None
        y = float(y_match.group(1)) if y_match else None
        z = float(z_match.group(1)) if z_match else None
        
        is_relative = 'G91' in gcode_line.upper()
        
        if is_relative:
            valid, rel_errors = self.validate_relative_move(x, y, z)
        else:
            valid, rel_errors = self.validate_absolute_move(x, y, z)
        
        if not valid:
            errors.extend(rel_errors)
        
        return len(errors) == 0, errors
    
    def get_safe_zone_info(self) -> Dict:
        """Get information about safe zone boundaries."""
        return {
            'enabled': self.enable_limits,
            'safety_margin': self.safety_margin,
            'x': {
                'min': self.safe_x_min,
                'max': self.safe_x_max,
                'hard_min': self.specs['x_min'],
                'hard_max': self.specs['x_max'],
            },
            'y': {
                'min': self.safe_y_min,
                'max': self.safe_y_max,
                'hard_min': self.specs['y_min'],
                'hard_max': self.specs['y_max'],
            },
            'z': {
                'min': self.safe_z_min,
                'max': self.safe_z_max,
                'hard_min': self.specs['z_min'],
                'hard_max': self.specs['z_max'],
            },
            'current_position': self.current_pos.copy(),
        }
    
    def get_distance_to_limits(self) -> Dict:
        """Get distance from current position to each limit."""
        return {
            'x_to_min': self.current_pos['x'] - self.safe_x_min,
            'x_to_max': self.safe_x_max - self.current_pos['x'],
            'y_to_min': self.current_pos['y'] - self.safe_y_min,
            'y_to_max': self.safe_y_max - self.current_pos['y'],
            'z_to_min': self.current_pos['z'] - self.safe_z_min,
            'z_to_max': self.safe_z_max - self.current_pos['z'],
        }
