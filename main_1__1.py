import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library - Личная кинотека")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Путь к файлу данных
        self.data_file = "movies.json"
        
        # Список фильмов
        self.movies = []
        
        # Список жанров для выпадающего списка
        self.genres = [
            "Боевик", "Комедия", "Драма", "Ужасы", "Фантастика",
            "Фэнтези", "Триллер", "Мелодрама", "Детектив", "Приключения",
            "Мультфильм", "Документальный", "Исторический", "Военный"
        ]
        
        # Загружаем данные при запуске
        self.load_movies()
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Обновляем таблицу
        self.update_table()
    
    def create_widgets(self):
        # Фрейм для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавление фильма", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Название фильма
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w", pady=2)
        self.title_entry = ttk.Entry(input_frame, width=40)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Жанр
        ttk.Label(input_frame, text="Жанр:").grid(row=1, column=0, sticky="w", pady=2)
        self.genre_combo = ttk.Combobox(input_frame, values=self.genres, width=37)
        self.genre_combo.grid(row=1, column=1, padx=5, pady=2)
        self.genre_combo.set(self.genres[0])
        
        # Год выпуска
        ttk.Label(input_frame, text="Год выпуска:").grid(row=2, column=0, sticky="w", pady=2)
        self.year_entry = ttk.Entry(input_frame, width=40)
        self.year_entry.grid(row=2, column=1, padx=5, pady=2)
        
        # Рейтинг
        ttk.Label(input_frame, text="Рейтинг (0-10):").grid(row=3, column=0, sticky="w", pady=2)
        self.rating_entry = ttk.Entry(input_frame, width=40)
        self.rating_entry.grid(row=3, column=1, padx=5, pady=2)
        
        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить фильм", command=self.add_movie).grid(
            row=4, column=0, columnspan=2, pady=10
        )
        
        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding="10")
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по жанру
        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, sticky="w")
        self.filter_genre = ttk.Combobox(filter_frame, values=["Все"] + self.genres, width=20)
        self.filter_genre.grid(row=0, column=1, padx=5)
        self.filter_genre.set("Все")
        self.filter_genre.bind("«ComboboxSelected»", self.apply_filters)
        
        # Фильтр по году
        ttk.Label(filter_frame, text="Год от:").grid(row=0, column=2, sticky="w", padx=(20,0))
        self.filter_year_from = ttk.Entry(filter_frame, width=10)
        self.filter_year_from.grid(row=0, column=3, padx=5)
        
        ttk.Label(filter_frame, text="до:").grid(row=0, column=4, sticky="w")
        self.filter_year_to = ttk.Entry(filter_frame, width=10)
        self.filter_year_to.grid(row=0, column=5, padx=5)
        
        # Кнопки фильтрации
        ttk.Button(filter_frame, text="Применить фильтры", command=self.apply_filters).grid(
            row=0, column=6, padx=10
        )
        ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters).grid(
            row=0, column=7, padx=5
        )
        
        # Таблица для отображения фильмов
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создаем Treeview
        columns = ("Название", "Жанр", "Год", "Рейтинг")
        self.


tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Определяем заголовки
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        
        # Добавляем scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещаем таблицу и scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(button_frame, text="Удалить выбранный фильм", command=self.delete_movie).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Экспорт в JSON", command=self.save_movies).pack(
            side="left", padx=5
        )
        
        # Статистика
        self.stats_label = ttk.Label(button_frame, text="")
        self.stats_label.pack(side="right", padx=5)
    
    def validate_input(self, title, genre, year_str, rating_str):
        """Проверка корректности ввода"""
        errors = []
        
        # Проверка названия
        if not title.strip():
            errors.append("Название фильма не может быть пустым")
        
        # Проверка года
        try:
            year = int(year_str)
            if year < 1888 or year > datetime.now().year:
                errors.append(f"Год должен быть между 1888 и {datetime.now().year}")
        except ValueError:
            errors.append("Год должен быть числом")
        
        # Проверка рейтинга
        try:
            rating = float(rating_str)
            if rating < 0 or rating > 10:
                errors.append("Рейтинг должен быть от 0 до 10")
        except ValueError:
            errors.append("Рейтинг должен быть числом от 0 до 10")
        
        return errors
    
    def add_movie(self):
        """Добавление нового фильма"""
        title = self.title_entry.get()
        genre = self.genre_combo.get()
        year_str = self.year_entry.get()
        rating_str = self.rating_entry.get()
        
        # Валидация
        errors = self.validate_input(title, genre, year_str, rating_str)
        if errors:
            messagebox.showerror("Ошибка ввода", "\n".join(errors))
            return
        
        # Создаем объект фильма
        movie = {
            "title": title.strip(),
            "genre": genre,
            "year": int(year_str),
            "rating": float(rating_str)
        }
        
        # Добавляем в список
        self.movies.append(movie)
        
        # Очищаем поля ввода
        self.title_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)
        
        # Сохраняем и обновляем таблицу
        self.save_movies()
        self.update_table()
        
        messagebox.showinfo("Успех", f"Фильм '{title}' добавлен в библиотеку!")
    
    def delete_movie(self):
        """Удаление выбранного фильма"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите фильм для удаления")
            return
        
        # Получаем индекс выбранного элемента
        item = self.tree.item(selected[0])
        values = item['values']
        
        # Ищем и удаляем фильм
        for i, movie in enumerate(self.movies):
            if (movie['title'] == values[0] and 
                movie['genre'] == values[1] and 
                movie['year'] == values[2] and 
                movie['rating'] == values[3]):
                
                if messagebox.askyesno("Подтверждение", 
                    f"Вы действительно хотите удалить фильм '{movie['title']}'?"):
                    del self.movies[i]
                    self.save_movies()


self.update_table()
                    messagebox.showinfo("Успех", "Фильм удален!")
                break
    
    def apply_filters(self, event=None):
        """Применение фильтров"""
        self.update_table()
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.filter_genre.set("Все")
        self.filter_year_from.delete(0, tk.END)
        self.filter_year_to.delete(0, tk.END)
        self.update_table()
    
    def get_filtered_movies(self):
        """Получение отфильтрованного списка фильмов"""
        filtered = self.movies[:]
        
        # Фильтр по жанру
        genre_filter = self.filter_genre.get()
        if genre_filter != "Все" and genre_filter:
            filtered = [m for m in filtered if m['genre'] == genre_filter]
        
        # Фильтр по году
        year_from = self.filter_year_from.get()
        year_to = self.filter_year_to.get()
        
        if year_from:
            try:
                year_from = int(year_from)
                filtered = [m for m in filtered if m['year'] >= year_from]
            except ValueError:
                pass
        
        if year_to:
            try:
                year_to = int(year_to)
                filtered = [m for m in filtered if m['year'] <= year_to]
            except ValueError:
                pass
        
        return filtered
    
    def update_table(self):
        """Обновление таблицы с фильмами"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получаем отфильтрованные данные
        filtered_movies = self.get_filtered_movies()
        
        # Заполняем таблицу
        for movie in filtered_movies:
            self.tree.insert("", "end", values=(
                movie['title'],
                movie['genre'],
                movie['year'],
                movie['rating']
            ))
        
        # Обновляем статистику
        self.update_stats(filtered_movies)
    
    def update_stats(self, movies):
        """Обновление статистики"""
        if not movies:
            self.stats_label.config(text="Фильмов: 0 | Средний рейтинг: 0.0")
            return
        
        total_movies = len(movies)
        avg_rating = sum(movie['rating'] for movie in movies) / total_movies
        
        self.stats_label.config(text=f"Фильмов: {total_movies} | Средний рейтинг: {avg_rating:.1f}")
    
    def save_movies(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
    
    def load_movies(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.movies = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
                self.movies = []
        else:
            # Создаем примеры фильмов для демонстрации
            self.movies = [
                {
                    "title": "Побег из Шоушенка",
                    "genre": "Драма",
                    "year": 1994,
                    "rating": 9.1
                },
                {
                    "title": "Крестный отец",
                    "genre": "Драма",
                    "year": 1972,
                    "rating": 9.2
                },
                {
                    "title": "Темный рыцарь",
                    "genre": "Боевик",
                    "year": 2008,
                    "rating": 9.0
                }
            ]
            self.save_movies()

def main():
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()

if __nam


e__ == "__main__":
    main()
   

  
