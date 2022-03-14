
/// <summary>
/// Some Documentation
/// </summary>
/// <remarks>
/// Some remarks?
/// </remarks>
public abstract class Bar<T> 
    where T : str {
    /// <summary> Bar Member  </summary>
    public static readonly int bar = 0;
    /// <summary> Bar Method  </summary>
    public abstract void barred(float b) {}
}

/// <summary>
/// Some Documentation
/// </summary>
class Bar2 : Bar {

}