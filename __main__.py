
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

class RecursiveHyperSpace:
    def __init__(self, limit_dimensions=6, system_length=12, base_slope=0.25, slope_growth=0.15, angle_step=45):
        """
        :param limit_dimensions: The maximum number of coordinates the system accepts (e.g. 5 means x,y,z,d4,d5).
        """
        self.limit_dims = limit_dimensions
        self.h = system_length
        self.base_slope = base_slope
        self.slope_growth = slope_growth
        self.angle_step = angle_step
        
        self.points_data = [] 
        self.max_dims_used = 0 

    def _calculate_cone_slope(self, dim_index_offset):
        return self.base_slope + (self.slope_growth * (dim_index_offset + 1))

    def add_point(self, coords, label="Point"):
        # --- NEW VALIDATION LOGIC ---
        input_dim_count = len(coords)
        
        # Check if point exceeds the system limit
        if input_dim_count > self.limit_dims:
            print(f"⚠️  WARNING: Point '{label}' has {input_dim_count} dimensions.")
            print(f"    System limit is {self.limit_dims}. Truncating extra coordinates.")
            # Truncate the list to fit the system
            coords = coords[:self.limit_dims]
            
        # Basic check for 3D
        if len(coords) < 3:
            print(f"❌ Error: Point {label} is too small (needs at least x,y,z).")
            return

        # Standard Processing
        base_pos = np.array(coords[0:3], dtype=float)
        extra_dims = coords[3:]
        
        # Track max dims for drawing (only up to the limit)
        if len(extra_dims) > self.max_dims_used:
            self.max_dims_used = len(extra_dims)

        trace_steps = []    
        vector_lines = []   
        
        current_pos = base_pos.copy()
        trace_steps.append({'pos': current_pos.copy(), 'label': f"{label} (3D)"})
        
        for i, magnitude in enumerate(extra_dims):
            dim_id = 4 + i
            deg_angle = 90 + (self.angle_step * i)
            rad_angle = np.deg2rad(deg_angle)
            
            dy = magnitude * np.cos(rad_angle)
            dz = magnitude * np.sin(rad_angle)
            vector = np.array([0.0, dy, dz])
            
            prev_pos = current_pos.copy()
            candidate_pos = prev_pos + vector
            
            this_cone_slope = self._calculate_cone_slope(i)
            current_x = candidate_pos[0]
            max_radius = abs(current_x) * this_cone_slope
            current_r = np.sqrt(candidate_pos[1]**2 + candidate_pos[2]**2)
            
            status = ""
            if current_r > max_radius:
                scale = max_radius / current_r
                candidate_pos[1] *= scale
                candidate_pos[2] *= scale
                status = "(Clamped)"
                
            current_pos = candidate_pos
            
            trace_steps.append({'pos': current_pos.copy(), 'label': f"D{dim_id} {status}"})
            vector_lines.append({
                'start': prev_pos,
                'end': current_pos,
                'name': f"D{dim_id} Vector"
            })
            
        self.points_data.append({
            'label': label,
            'trace': trace_steps,
            'vectors': vector_lines
        })

    def add_points_from_list(self, list_of_points):
        for i, p_coords in enumerate(list_of_points):
            self.add_point(p_coords, label=f"BatchPoint_{i+1}")

    def draw(self):
        fig = go.Figure()
        
        # 1. DRAW CONES
        u = np.linspace(0, 2 * np.pi, 60)
        v = np.linspace(0, self.h, 40)
        U, V = np.meshgrid(u, v)
        
        # Base 3D
        R3 = V * self.base_slope
        Y3 = R3 * np.cos(U)
        Z3 = R3 * np.sin(U)
        fig.add_trace(go.Surface(
            x=V, y=Y3, z=Z3, 
            opacity=0.1, colorscale='Blues', showscale=False, name='3D Base'
        ))
        
        # Extra Cones
        colors = ['Reds', 'Greens', 'Purples', 'Oranges', 'Teal']
        for i in range(self.max_dims_used):
            slope = self._calculate_cone_slope(i)
            Rc = V * slope
            Yc = Rc * np.cos(U)
            Zc = Rc * np.sin(U)
            c_name = colors[i % len(colors)]
            fig.add_trace(go.Surface(
                x=V, y=Yc, z=Zc, 
                opacity=0.05, colorscale=c_name, showscale=False, name=f'Cone D{4+i}'
            ))

        # 2. DRAW POINTS
        for pt in self.points_data:
            for vec in pt['vectors']:
                fig.add_trace(go.Scatter3d(
                    x=[vec['start'][0], vec['end'][0]],
                    y=[vec['start'][1], vec['end'][1]],
                    z=[vec['start'][2], vec['end'][2]],
                    mode='lines', line=dict(width=5),
                    name=f"{pt['label']} Path"
                ))
            
            final_pos = pt['trace'][-1]['pos']
            fig.add_trace(go.Scatter3d(
                x=[final_pos[0]], y=[final_pos[1]], z=[final_pos[2]],
                mode='markers', marker=dict(size=8, symbol='diamond'),
                name=f"{pt['label']} Final"
            ))

        fig.update_layout(
            title=f"System Limit: {self.limit_dims} Dimensions",
            scene=dict(
                xaxis=dict(range=[0, self.h], title="X"),
                yaxis=dict(range=[-10, 10], title="Y"),
                zaxis=dict(range=[-10, 10], title="Z"),
                aspectmode='data'
            ),
            margin=dict(l=0, r=0, b=0, t=40)
        )
        
        pio.write_html(fig, file='safe_hyperspace.html', auto_open=True)
        print("Drawing generated.")


# ==========================================
#        TESTING THE WARNING SYSTEM
# ==========================================
if __name__ == "__main__":
    
    # 1. CREATE A SYSTEM LIMITED TO 5 DIMENSIONS (X, Y, Z, D4, D5)
    hs = RecursiveHyperSpace(limit_dimensions=5)
    
    print("--- TEST START ---")
    
    # 2. ADD A VALID POINT (5 coords) -> Should work silently
    hs.add_point([8, 0, 0, 2, 20], label="Valid Point")
    hs.add_point([8, 0, 0, 2, -20], label="Valid Point")
    
    # 3. ADD AN INVALID POINT (7 coords) -> Should Trigger Warning
    # It has X,Y,Z, D4, D5, D6, D7
    # The system should keep D4, D5 and throw away D6, D7
    hs.add_point([8, 0, 0, 2, 2, 99, 99], label="Overloaded Point")
    
    print("--- TEST END ---")
    
    hs.draw()