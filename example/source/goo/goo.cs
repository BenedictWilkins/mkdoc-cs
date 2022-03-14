struct goop {
    public int x = 0;
}

namespace Foos {

    namespace Goos {

        interface IGloo {

        }

        interface IGloo2 {

        }

        class Gloo : IGloo, IGloo2 {
            public float y = 0f;
        }

        namespace Boos {

            class bloo {
                public float z = 10f;
            }
        }

        
    }
}

namespace Aloos {

    class Aloo {

    }
}