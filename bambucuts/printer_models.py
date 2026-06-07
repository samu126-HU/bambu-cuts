"""
Printer model definitions with specifications and limits.

This module defines the specifications for different Bambu Lab printer models,
including axis limits, speeds, and other hardware constraints.
"""

PRINTER_MODELS = {
    'A1_MINI': {
        'name': 'Bambu Lab A1 mini',
        'model_code': 'A1_MINI',
        'x_min': 0,
        'x_max': 165,
        'y_min': 0,
        'y_max': 190,
        'z_min': 0,
        'z_max': 150,
        'print_speed_max': 150,
        'nozzle_diameter': 0.4,
        'build_plate': 'PEI Spring',
    },
    'A1': {
        'name': 'Bambu Lab A1',
        'model_code': 'A1',
        'x_min': 0,
        'x_max': 256,
        'y_min': 0,
        'y_max': 256,
        'z_min': 0,
        'z_max': 165,
        'print_speed_max': 150,
        'nozzle_diameter': 0.4,
        'build_plate': 'PEI Spring',
    },
}

DEFAULT_MODEL = 'A1_MINI'


def get_printer_model(model_key):
    """
    Get printer model specifications.
    
    Args:
        model_key: Model identifier (e.g., 'A1_MINI', 'A1')
        
    Returns:
        Dictionary with printer specifications
    """
    return PRINTER_MODELS.get(model_key, PRINTER_MODELS[DEFAULT_MODEL])


def list_available_models():
    """Get list of available printer models."""
    return [
        {
            'key': key,
            'name': specs['name'],
            'x_max': specs['x_max'],
            'y_max': specs['y_max'],
            'z_max': specs['z_max'],
        }
        for key, specs in PRINTER_MODELS.items()
    ]


def validate_model_key(model_key):
    """Check if model key is valid."""
    return model_key in PRINTER_MODELS
