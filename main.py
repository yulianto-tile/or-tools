from fastapi import FastAPI
from pydantic import BaseModel
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np

app = FastAPI(title="Sistem Penjadwalan Skripsi Mahasiswa Berbasis Google OR-Tools", version="1.0.0")

class DistanceMatrix(BaseModel):
    matrix: list[list[float]]
    num_vehicles: int = 1
    depot: int = 0

@app.get("/")
def read_root():
    return {
        "message": "Sistem Penjadwalan Skripsi Mahasiswa Berbasis Google OR-Tools",
        "status": "running",
        "ortools_version": "9.8.3296"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/solve-vrp")
def solve_vehicle_routing(data: DistanceMatrix):
    """
    Menyelesaikan Vehicle Routing Problem (VRP) sederhana
    """
    try:
        # Buat data model
        distance_matrix = data.matrix
        num_vehicles = data.num_vehicles
        depot = data.depot
        
        # Buat Routing Index Manager
        manager = pywrapcp.RoutingIndexManager(
            len(distance_matrix),
            num_vehicles,
            depot
        )
        
        # Buat Routing Model
        routing = pywrapcp.RoutingModel(manager)
        
        # Buat callback untuk distance
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(distance_matrix[from_node][to_node])
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Setting search parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        
        # Solve
        solution = routing.SolveWithParameters(search_parameters)
        
        if solution:
            routes = []
            total_distance = 0
            
            for vehicle_id in range(num_vehicles):
                route = []
                index = routing.Start(vehicle_id)
                route_distance = 0
                
                while not routing.IsEnd(index):
                    node = manager.IndexToNode(index)
                    route.append(node)
                    previous_index = index
                    index = solution.Value(routing.NextVar(index))
                    route_distance += routing.GetArcCostForVehicle(
                        previous_index, index, vehicle_id
                    )
                
                route.append(manager.IndexToNode(index))
                routes.append({
                    "vehicle": vehicle_id,
                    "route": route,
                    "distance": route_distance
                })
                total_distance += route_distance
            
            return {
                "status": "success",
                "total_distance": total_distance,
                "routes": routes
            }
        else:
            return {
                "status": "failed",
                "message": "No solution found"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/solve-linear")
def solve_linear_optimization(variables: dict):
    """
    Contoh simple linear programming
    """
    try:
        from ortools.linear_solver import pywraplp
        
        # Buat solver
        solver = pywraplp.Solver.CreateSolver('GLOP')
        
        if not solver:
            return {"status": "error", "message": "Solver not available"}
        
        # Contoh: Maksimalkan 3x + y
        # Subject to: x + 2y <= 14, 3x - y >= 0, x - y <= 2
        x = solver.NumVar(0, solver.infinity(), 'x')
        y = solver.NumVar(0, solver.infinity(), 'y')
        
        # Constraints
        solver.Add(x + 2 * y <= 14)
        solver.Add(3 * x - y >= 0)
        solver.Add(x - y <= 2)
        
        # Objective
        solver.Maximize(3 * x + y)
        
        status = solver.Solve()
        
        if status == pywraplp.Solver.OPTIMAL:
            return {
                "status": "optimal",
                "x": x.solution_value(),
                "y": y.solution_value(),
                "objective_value": solver.Objective().Value()
            }
        else:
            return {"status": "no_solution"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}