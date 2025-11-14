package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/joho/godotenv"
	_ "github.com/lib/pq"
)

var db *sql.DB

// Models
type Item struct {
	ID          int       `json:"id"`
	Title       string    `json:"title"`
	Description string    `json:"description"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

type CreateItemRequest struct {
	Title       string `json:"title"`
	Description string `json:"description"`
}

type HealthResponse struct {
	Status   string `json:"status"`
	Database string `json:"database"`
	Time     string `json:"time"`
}

// Database initialization
func initDB() error {
	var err error

	// Get database connection string from environment
	dbHost := getEnv("DB_HOST", "localhost")
	dbPort := getEnv("DB_PORT", "5432")
	dbUser := getEnv("DB_USER", "postgres")
	dbPassword := getEnv("DB_PASSWORD", "postgres")
	dbName := getEnv("DB_NAME", "neevs")

	connStr := fmt.Sprintf(
		"host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		dbHost, dbPort, dbUser, dbPassword, dbName,
	)

	db, err = sql.Open("postgres", connStr)
	if err != nil {
		return fmt.Errorf("failed to open database: %w", err)
	}

	// Test connection
	if err = db.Ping(); err != nil {
		return fmt.Errorf("failed to ping database: %w", err)
	}

	// Create tables if they don't exist
	if err = createTables(); err != nil {
		return fmt.Errorf("failed to create tables: %w", err)
	}

	log.Println("✅ Database connected successfully")
	return nil
}

func createTables() error {
	query := `
	CREATE TABLE IF NOT EXISTS items (
		id SERIAL PRIMARY KEY,
		title VARCHAR(255) NOT NULL,
		description TEXT,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	CREATE INDEX IF NOT EXISTS idx_items_created_at ON items(created_at DESC);
	`

	_, err := db.Exec(query)
	return err
}

// Handlers
func healthCheck(c *fiber.Ctx) error {
	dbStatus := "connected"
	if err := db.Ping(); err != nil {
		dbStatus = "disconnected"
	}

	return c.JSON(HealthResponse{
		Status:   "ok",
		Database: dbStatus,
		Time:     time.Now().Format(time.RFC3339),
	})
}

func getItems(c *fiber.Ctx) error {
	rows, err := db.Query(`
		SELECT id, title, description, created_at, updated_at
		FROM items
		ORDER BY created_at DESC
		LIMIT 100
	`)
	if err != nil {
		log.Printf("Error querying items: %v", err)
		return c.Status(500).JSON(fiber.Map{
			"error": "Failed to fetch items",
		})
	}
	defer rows.Close()

	items := []Item{}
	for rows.Next() {
		var item Item
		err := rows.Scan(&item.ID, &item.Title, &item.Description, &item.CreatedAt, &item.UpdatedAt)
		if err != nil {
			log.Printf("Error scanning item: %v", err)
			continue
		}
		items = append(items, item)
	}

	return c.JSON(items)
}

func getItem(c *fiber.Ctx) error {
	id := c.Params("id")

	var item Item
	err := db.QueryRow(`
		SELECT id, title, description, created_at, updated_at
		FROM items
		WHERE id = $1
	`, id).Scan(&item.ID, &item.Title, &item.Description, &item.CreatedAt, &item.UpdatedAt)

	if err == sql.ErrNoRows {
		return c.Status(404).JSON(fiber.Map{
			"error": "Item not found",
		})
	}

	if err != nil {
		log.Printf("Error fetching item: %v", err)
		return c.Status(500).JSON(fiber.Map{
			"error": "Failed to fetch item",
		})
	}

	return c.JSON(item)
}

func createItem(c *fiber.Ctx) error {
	var req CreateItemRequest

	if err := c.BodyParser(&req); err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "Invalid request body",
		})
	}

	if req.Title == "" {
		return c.Status(400).JSON(fiber.Map{
			"error": "Title is required",
		})
	}

	var item Item
	err := db.QueryRow(`
		INSERT INTO items (title, description)
		VALUES ($1, $2)
		RETURNING id, title, description, created_at, updated_at
	`, req.Title, req.Description).Scan(&item.ID, &item.Title, &item.Description, &item.CreatedAt, &item.UpdatedAt)

	if err != nil {
		log.Printf("Error creating item: %v", err)
		return c.Status(500).JSON(fiber.Map{
			"error": "Failed to create item",
		})
	}

	return c.Status(201).JSON(item)
}

func updateItem(c *fiber.Ctx) error {
	id := c.Params("id")

	var req CreateItemRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(400).JSON(fiber.Map{
			"error": "Invalid request body",
		})
	}

	var item Item
	err := db.QueryRow(`
		UPDATE items
		SET title = $1, description = $2, updated_at = CURRENT_TIMESTAMP
		WHERE id = $3
		RETURNING id, title, description, created_at, updated_at
	`, req.Title, req.Description, id).Scan(&item.ID, &item.Title, &item.Description, &item.CreatedAt, &item.UpdatedAt)

	if err == sql.ErrNoRows {
		return c.Status(404).JSON(fiber.Map{
			"error": "Item not found",
		})
	}

	if err != nil {
		log.Printf("Error updating item: %v", err)
		return c.Status(500).JSON(fiber.Map{
			"error": "Failed to update item",
		})
	}

	return c.JSON(item)
}

func deleteItem(c *fiber.Ctx) error {
	id := c.Params("id")

	result, err := db.Exec("DELETE FROM items WHERE id = $1", id)
	if err != nil {
		log.Printf("Error deleting item: %v", err)
		return c.Status(500).JSON(fiber.Map{
			"error": "Failed to delete item",
		})
	}

	rows, _ := result.RowsAffected()
	if rows == 0 {
		return c.Status(404).JSON(fiber.Map{
			"error": "Item not found",
		})
	}

	return c.JSON(fiber.Map{
		"message": "Item deleted successfully",
	})
}

func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}

func main() {
	// Load .env file if it exists
	_ = godotenv.Load()

	// Initialize database
	if err := initDB(); err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
	defer db.Close()

	// Create Fiber app
	app := fiber.New(fiber.Config{
		AppName:      "Neevs Backend API v1.0",
		JSONEncoder:  json.Marshal,
		JSONDecoder:  json.Unmarshal,
	})

	// Middleware
	app.Use(logger.New())
	app.Use(cors.New(cors.Config{
		AllowOrigins: getEnv("CORS_ORIGINS", "*"),
		AllowHeaders: "Origin, Content-Type, Accept, Authorization",
		AllowMethods: "GET, POST, PUT, DELETE, OPTIONS",
	}))

	// Routes
	api := app.Group("/api")

	api.Get("/health", healthCheck)
	api.Get("/items", getItems)
	api.Get("/items/:id", getItem)
	api.Post("/items", createItem)
	api.Put("/items/:id", updateItem)
	api.Delete("/items/:id", deleteItem)

	// Start server
	port := getEnv("PORT", "3001")
	log.Printf("🚀 Server starting on port %s", port)
	log.Fatal(app.Listen(":" + port))
}
