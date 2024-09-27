---
model: claude-3-5-sonnet-20240620
system: '{sys_python_prefs} Only speak in French'
options:
  max_tokens: 4096
---

# %User

Give me a python function to add two numbers.

# %Assistant

Voici une fonction Python pour additionner deux nombres :

```python
def ajouter(a: float | int, b: float | int) -> float:
    """
    Additionne deux nombres.

    Parameters
    ----------
    a : float | int
        Le premier nombre.
    b : float | int
        Le deuxième nombre.

    Returns
    -------
    float
        La somme des deux nombres.

    Examples
    --------
    >>> ajouter(2, 3)
    5.0
    >>> ajouter(2.5, 3.7)
    6.2
    """
    return float(a + b)
```